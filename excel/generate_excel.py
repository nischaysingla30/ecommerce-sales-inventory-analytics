import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure excel directory exists
os.makedirs('../reports', exist_ok=True)

print("Starting Optimized Excel workbook generation...")

# -----------------------------------------------------------------------------
# 1. LOAD CLEANED DATA
# -----------------------------------------------------------------------------
df_categories = pd.read_csv('../data/processed/categories.csv')
df_products = pd.read_csv('../data/processed/products.csv')
df_customers = pd.read_csv('../data/processed/customers.csv')
df_orders = pd.read_csv('../data/processed/orders.csv')
df_order_items = pd.read_csv('../data/processed/order_items.csv')
df_inventory = pd.read_csv('../data/processed/inventory.csv')

# -----------------------------------------------------------------------------
# 2. ADD FORMULA STRINGS FOR ORDER ITEMS (Calculated columns in Excel)
# -----------------------------------------------------------------------------
print("Adding Excel formulas to Order_Items dataframe...")

num_items = len(df_order_items)
formulas = {
    "retail_price": [],
    "cost_price": [],
    "gross_revenue": [],
    "discount_amount": [],
    "net_revenue": [],
    "total_cost": [],
    "profit": [],
    "category_id": [],
    "region": []
}

# In Excel, the row indexing starts from 2 since row 1 is header
for i in range(2, num_items + 2):
    # C is product_id, D is quantity, E is discount_pct, F is return_status, B is order_id
    formulas["retail_price"].append(f"=XLOOKUP(C{i}, Products!$A$2:$A$101, Products!$E$2:$E$101)")
    formulas["cost_price"].append(f"=XLOOKUP(C{i}, Products!$A$2:$A$101, Products!$D$2:$D$101)")
    formulas["gross_revenue"].append(f"=D{i}*G{i}")
    formulas["discount_amount"].append(f"=I{i}*E{i}")
    formulas["net_revenue"].append(f"=I{i}-J{i}")
    formulas["total_cost"].append(f"=D{i}*H{i}")
    formulas["profit"].append(f"=IF(F{i}=1, -L{i}, K{i}-L{i})")
    formulas["category_id"].append(f"=XLOOKUP(C{i}, Products!$A$2:$A$101, Products!$C$2:$C$101)")
    formulas["region"].append(f"=XLOOKUP(B{i}, Orders!$A$2:$A$60005, Orders!$F$2:$F$60005)")

df_order_items["retail_price"] = formulas["retail_price"]
df_order_items["cost_price"] = formulas["cost_price"]
df_order_items["gross_revenue"] = formulas["gross_revenue"]
df_order_items["discount_amount"] = formulas["discount_amount"]
df_order_items["net_revenue"] = formulas["net_revenue"]
df_order_items["total_cost"] = formulas["total_cost"]
df_order_items["profit"] = formulas["profit"]
df_order_items["category_id"] = formulas["category_id"]
df_order_items["region"] = formulas["region"]

# -----------------------------------------------------------------------------
# 3. WRITE DATA TO EXCEL
# -----------------------------------------------------------------------------
excel_path = '../reports/ECommerce_Sales_Inventory_Diagnostics.xlsx'
print(f"Writing tables to Excel workbook at {excel_path} (this may take 20-30 seconds)...")

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_order_items.to_excel(writer, sheet_name='Order_Items', index=False)
    df_orders.to_excel(writer, sheet_name='Orders', index=False)
    df_products.to_excel(writer, sheet_name='Products', index=False)
    df_customers.to_excel(writer, sheet_name='Customers', index=False)
    df_categories.to_excel(writer, sheet_name='Categories', index=False)
    df_inventory.to_excel(writer, sheet_name='Inventory', index=False)

# -----------------------------------------------------------------------------
# 4. FORMAT WORKBOOK & CREATE DASHBOARD
# -----------------------------------------------------------------------------
print("Loading workbook in openpyxl for formatting...")
wb = openpyxl.load_workbook(excel_path)

# Insert the KPI Dashboard sheet as the first tab
dash_sheet = wb.create_sheet(title="KPI Dashboard", index=0)

# Colors and styles
navy_header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
navy_accent_fill = PatternFill(start_color="F2F4F8", end_color="F2F4F8", fill_type="solid")
kpi_card_fill = PatternFill(start_color="D9E2EC", end_color="D9E2EC", fill_type="solid")
light_grey_fill = PatternFill(start_color="F7FAFC", end_color="F7FAFC", fill_type="solid")

font_title = Font(name="Segoe UI", size=18, bold=True, color="FFFFFF")
font_section = Font(name="Segoe UI", size=14, bold=True, color="1B365D")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_bold_dark = Font(name="Segoe UI", size=11, bold=True, color="1B365D")
font_regular = Font(name="Segoe UI", size=11, color="000000")
font_kpi_val = Font(name="Segoe UI", size=16, bold=True, color="1B365D")
font_kpi_lbl = Font(name="Segoe UI", size=9, bold=False, color="486581")

thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)
double_bottom_border = Border(
    bottom=Side(style='double', color='1B365D'),
    top=Side(style='thin', color='CCCCCC')
)

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

# Show gridlines for all sheets
for name in wb.sheetnames:
    wb[name].views.sheetView[0].showGridLines = True

# Create Banner Header in Dashboard
dash_sheet.merge_cells("A1:G3")
for r in range(1, 4):
    for c in range(1, 8):
        cell = dash_sheet.cell(row=r, column=c)
        cell.fill = navy_header_fill
header_cell = dash_sheet["A1"]
header_cell.value = "E-COMMERCE SALES & INVENTORY DASHBOARD"
header_cell.font = font_title
header_cell.alignment = align_center

# -----------------------------------------------------------------------------
# KPI CARDS Setup
# -----------------------------------------------------------------------------
kpi_definitions = [
    {"label": "Total Net Revenue", "formula": "=SUM(Order_Items!K2:K120000)", "col_start": 2, "format": "$#,##0.00"},
    {"label": "Total Cost of Goods", "formula": "=SUM(Order_Items!L2:L120000)", "col_start": 3, "format": "$#,##0.00"},
    {"label": "Total Net Profit", "formula": "=B6-C6", "col_start": 4, "format": "$#,##0.00"},
    {"label": "Profit Margin %", "formula": "=D6/B6", "col_start": 5, "format": "0.0%"},
    {"label": "Return Rate %", "formula": "=AVERAGE(Order_Items!F2:F120000)", "col_start": 6, "format": "0.0%"}
]

# Write KPI Cards
for kpi in kpi_definitions:
    col = kpi["col_start"]
    lbl_cell = dash_sheet.cell(row=5, column=col, value=kpi["label"])
    lbl_cell.font = font_kpi_lbl
    lbl_cell.fill = kpi_card_fill
    lbl_cell.alignment = align_center
    lbl_cell.border = thin_border
    
    val_cell = dash_sheet.cell(row=6, column=col, value=kpi["formula"])
    val_cell.font = font_kpi_val
    val_cell.fill = kpi_card_fill
    val_cell.alignment = align_center
    val_cell.number_format = kpi["format"]
    val_cell.border = thin_border

dash_sheet.row_dimensions[1].height = 20
dash_sheet.row_dimensions[2].height = 20
dash_sheet.row_dimensions[3].height = 20
dash_sheet.row_dimensions[5].height = 18
dash_sheet.row_dimensions[6].height = 30

# -----------------------------------------------------------------------------
# TABLE 1: CATEGORY SALES ANALYSIS (SUMIFS & XLOOKUP)
# -----------------------------------------------------------------------------
dash_sheet.cell(row=9, column=1, value="PRODUCT CATEGORY ANALYSIS").font = font_section

headers_cat = ["Category ID", "Category Name", "Net Revenue", "Total Cost", "Net Profit", "Margin %"]
for idx, h in enumerate(headers_cat, 1):
    cell = dash_sheet.cell(row=10, column=idx, value=h)
    cell.font = font_header
    cell.fill = navy_header_fill
    cell.alignment = align_center
    cell.border = thin_border

# Populate Category Data
for cat_id in range(1, 6):
    r = 10 + cat_id
    dash_sheet.cell(row=r, column=1, value=cat_id).font = font_regular
    dash_sheet.cell(row=r, column=2, value=f"=XLOOKUP(A{r}, Categories!$A$2:$A$6, Categories!$B$2:$B$6)").font = font_regular
    
    c_rev = dash_sheet.cell(row=r, column=3, value=f"=SUMIFS(Order_Items!$K$2:$K$120000, Order_Items!$N$2:$N$120000, A{r})")
    c_rev.number_format = "$#,##0.00"
    c_rev.font = font_regular
    
    c_cost = dash_sheet.cell(row=r, column=4, value=f"=SUMIFS(Order_Items!$L$2:$L$120000, Order_Items!$N$2:$N$120000, A{r})")
    c_cost.number_format = "$#,##0.00"
    c_cost.font = font_regular
    
    c_prof = dash_sheet.cell(row=r, column=5, value=f"=C{r}-D{r}")
    c_prof.number_format = "$#,##0.00"
    c_prof.font = font_regular
    
    c_marg = dash_sheet.cell(row=r, column=6, value=f"=E{r}/C{r}")
    c_marg.number_format = "0.0%"
    c_marg.font = font_regular

    for col_idx in range(1, 7):
        dash_sheet.cell(row=r, column=col_idx).border = thin_border

# Totals Row for Category Table
total_row_idx = 16
dash_sheet.cell(row=total_row_idx, column=1, value="Total").font = font_bold_dark
dash_sheet.cell(row=total_row_idx, column=2, value="").font = font_bold_dark
dash_sheet.cell(row=total_row_idx, column=3, value="=SUM(C11:C15)").number_format = "$#,##0.00"
dash_sheet.cell(row=total_row_idx, column=3).font = font_bold_dark
dash_sheet.cell(row=total_row_idx, column=4, value="=SUM(D11:D15)").number_format = "$#,##0.00"
dash_sheet.cell(row=total_row_idx, column=4).font = font_bold_dark
dash_sheet.cell(row=total_row_idx, column=5, value="=SUM(E11:E15)").number_format = "$#,##0.00"
dash_sheet.cell(row=total_row_idx, column=5).font = font_bold_dark
dash_sheet.cell(row=total_row_idx, column=6, value="=E16/C16").number_format = "0.0%"
dash_sheet.cell(row=total_row_idx, column=6).font = font_bold_dark

for col_idx in range(1, 7):
    dash_sheet.cell(row=total_row_idx, column=col_idx).border = double_bottom_border

# -----------------------------------------------------------------------------
# TABLE 2: REGIONAL PERFORMANCE
# -----------------------------------------------------------------------------
dash_sheet.cell(row=19, column=1, value="REGIONAL SALES PERFORMANCE").font = font_section

headers_reg = ["Region", "Net Revenue", "Total Orders", "Average Order Value", "Cancelled Orders"]
for idx, h in enumerate(headers_reg, 1):
    cell = dash_sheet.cell(row=20, column=idx, value=h)
    cell.font = font_header
    cell.fill = navy_header_fill
    cell.alignment = align_center
    cell.border = thin_border

regions_list = ["East", "West", "South", "Midwest"]
for idx, reg in enumerate(regions_list):
    r = 21 + idx
    dash_sheet.cell(row=r, column=1, value=reg).font = font_regular
    
    # Net Revenue SUMIFS from Order_Items referencing region column O
    c_rev = dash_sheet.cell(row=r, column=2, value=f'=SUMIFS(Order_Items!$K$2:$K$120000, Order_Items!$O$2:$O$120000, A{r})')
    c_rev.number_format = "$#,##0.00"
    c_rev.font = font_regular
    
    # Total Orders COUNTIFS from Orders
    c_ord = dash_sheet.cell(row=r, column=3, value=f'=COUNTIFS(Orders!$F$2:$F$60005, A{r})')
    c_ord.number_format = "#,##0"
    c_ord.font = font_regular
    
    # Average Order Value
    c_aov = dash_sheet.cell(row=r, column=4, value=f'=B{r}/C{r}')
    c_aov.number_format = "$#,##0.00"
    c_aov.font = font_regular
    
    # Cancelled Orders
    c_can = dash_sheet.cell(row=r, column=5, value=f'=COUNTIFS(Orders!$F$2:$F$60005, A{r}, Orders!$E$2:$E$60005, "Cancelled")')
    c_can.number_format = "#,##0"
    c_can.font = font_regular

    for col_idx in range(1, 6):
        dash_sheet.cell(row=r, column=col_idx).border = thin_border

# Totals Row for Regional Table
total_reg_idx = 25
dash_sheet.cell(row=total_reg_idx, column=1, value="Total").font = font_bold_dark
dash_sheet.cell(row=total_reg_idx, column=2, value="=SUM(B21:B24)").number_format = "$#,##0.00"
dash_sheet.cell(row=total_reg_idx, column=2).font = font_bold_dark
dash_sheet.cell(row=total_reg_idx, column=3, value="=SUM(C21:C24)").number_format = "#,##0"
dash_sheet.cell(row=total_reg_idx, column=3).font = font_bold_dark
dash_sheet.cell(row=total_reg_idx, column=4, value="=B25/C25").number_format = "$#,##0.00"
dash_sheet.cell(row=total_reg_idx, column=4).font = font_bold_dark
dash_sheet.cell(row=total_reg_idx, column=5, value="=SUM(E21:E24)").number_format = "#,##0"
dash_sheet.cell(row=total_reg_idx, column=5).font = font_bold_dark

for col_idx in range(1, 6):
    dash_sheet.cell(row=total_reg_idx, column=col_idx).border = double_bottom_border

# -----------------------------------------------------------------------------
# COLUMN WIDTHS & HEADER STYLING (OPTIMIZED)
# -----------------------------------------------------------------------------
print("Formatting worksheet headers and column widths efficiently...")

for name in wb.sheetnames:
    ws = wb[name]
    
    # 1. Format Headers (Row 1) for all sheets except Dashboard
    if name != "KPI Dashboard":
        # Format the header row
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = font_header
            cell.fill = navy_header_fill
            cell.alignment = align_center

    # 2. Adjust Column Widths based on headers and first 100 rows (avoids scanning millions of cells)
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col[:100]:
            if cell.value:
                # Truncate representation for length check if formula
                val_str = str(cell.value)
                if val_str.startswith('='):
                    val_str = "Formula_Field"
                max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

# Save the workbook (this executes formulas and compresses the sheet)
print(f"Saving final Excel workbook (this will take 20-30 seconds)...")
wb.save(excel_path)
print(f"Excel workbook formatted and saved successfully to {excel_path}!")
