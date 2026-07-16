import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Try to import seaborn for prettier charts, fallback if not available
try:
    import seaborn as sns
    sns.set_theme(style="whitegrid")
except ImportError:
    sns = None

# Ensure the visual output folder exists
os.makedirs('../reports/visuals', exist_ok=True)

print("Starting Exploratory Data Analysis (EDA)...")

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
# 2. COMBINE DATASETS FOR ANALYSIS
# -----------------------------------------------------------------------------
# Merge order items with products to get prices
df_merged = df_order_items.merge(df_products, on='product_id', how='left')
# Merge categories
df_merged = df_merged.merge(df_categories, on='category_id', how='left')
# Merge orders to get dates and locations
df_merged = df_merged.merge(df_orders, on='order_id', how='left')
# Merge customers to get segments
df_merged = df_merged.merge(df_customers, on=['customer_id', 'region'], how='left')

# Calculate Revenue, Cost, and Profit
# Revenue = Quantity * Retail Price * (1 - Discount %)
# Cost = Quantity * Cost Price
# Profit = Revenue - Cost
# Note: Returned orders do not generate actual net sales in final reports, 
# but for EDA we will look at Gross Revenue and check Return Rates separately.
df_merged['gross_revenue'] = df_merged['quantity'] * df_merged['retail_price']
df_merged['discount_amount'] = df_merged['gross_revenue'] * df_merged['discount_pct']
df_merged['net_revenue'] = df_merged['gross_revenue'] - df_merged['discount_amount']
df_merged['total_cost'] = df_merged['quantity'] * df_merged['cost_price']
df_merged['profit'] = np.where(df_merged['return_status'] == 1, 0 - df_merged['total_cost'], df_merged['net_revenue'] - df_merged['total_cost'])

# Filter out Cancelled/Returned orders for Net Sales analyses
df_sales = df_merged[~df_merged['status'].isin(['Cancelled', 'Returned'])].copy()

# -----------------------------------------------------------------------------
# CHART 1: MONTHLY SALES TREND (LINE CHART)
# -----------------------------------------------------------------------------
print("Creating Chart 1: Monthly Sales Trend...")
df_sales['order_month'] = pd.to_datetime(df_sales['order_date']).dt.to_period('M')
monthly_sales = df_sales.groupby('order_month')['net_revenue'].sum().reset_index()
monthly_sales['order_month_str'] = monthly_sales['order_month'].astype(str)

plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['order_month_str'], monthly_sales['net_revenue'] / 1000, marker='o', linewidth=2.5, color='#2b5c8f')
plt.title('Monthly Net Revenue Trend (2024 - 2025)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Revenue ($ Thousands)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('../reports/visuals/monthly_sales_trend.png', dpi=150)
plt.close()

# -----------------------------------------------------------------------------
# CHART 2: REVENUE AND PROFIT BY CATEGORY (BAR CHART)
# -----------------------------------------------------------------------------
print("Creating Chart 2: Category Revenue and Margin...")
category_summary = df_sales.groupby('category_name').agg(
    Revenue=('net_revenue', 'sum'),
    Profit=('profit', 'sum')
).reset_index()
category_summary['Margin %'] = (category_summary['Profit'] / category_summary['Revenue']) * 100

fig, ax1 = plt.subplots(figsize=(10, 6))

color_rev = '#1f77b4'
ax1.set_xlabel('Category', fontsize=12, labelpad=10)
ax1.set_ylabel('Net Revenue ($)', color=color_rev, fontsize=12)
bars = ax1.bar(category_summary['category_name'], category_summary['Revenue'], color=color_rev, alpha=0.7, width=0.5)
ax1.tick_params(axis='y', labelcolor=color_rev)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

ax2 = ax1.twinx()  
color_margin = '#d62728'
ax2.set_ylabel('Profit Margin %', color=color_margin, fontsize=12)
line = ax2.plot(category_summary['category_name'], category_summary['Margin %'], color=color_margin, marker='s', linewidth=2, label='Margin %')
ax2.tick_params(axis='y', labelcolor=color_margin)

plt.title('Net Revenue & Profit Margin % by Product Category', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.savefig('../reports/visuals/category_performance.png', dpi=150)
plt.close()

# -----------------------------------------------------------------------------
# CHART 3: REGIONAL REVENUE BY CUSTOMER SEGMENT (STACKED/GROUPED BAR)
# -----------------------------------------------------------------------------
print("Creating Chart 3: Regional Sales by Segment...")
reg_seg_sales = df_sales.groupby(['region', 'customer_segment'])['net_revenue'].sum().unstack()

ax = reg_seg_sales.plot(kind='bar', figsize=(10, 6), color=['#2b5c8f', '#4682b4', '#87cefa'], edgecolor='grey')
plt.title('Regional Net Revenue by Customer Segment', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Region', fontsize=12)
plt.ylabel('Net Revenue ($)', fontsize=12)
plt.xticks(rotation=0)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
plt.legend(title='Customer Segment', frameon=True)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('../reports/visuals/regional_segment_sales.png', dpi=150)
plt.close()

# -----------------------------------------------------------------------------
# CHART 4: INVENTORY REORDER ALERTS STATUS (DONUT CHART)
# -----------------------------------------------------------------------------
print("Creating Chart 4: Inventory Restock Status...")
# stock levels vs. reorder point
df_inventory['needs_reorder'] = np.where(df_inventory['stock_level'] <= df_inventory['reorder_point'], 'Restock Alert', 'Healthy Stock')
status_counts = df_inventory['needs_reorder'].value_counts()

plt.figure(figsize=(7, 7))
colors = ['#2ca02c', '#d62728'] if status_counts.index[0] == 'Healthy Stock' else ['#d62728', '#2ca02c']
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, 
        colors=colors, wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title('Inventory Stock Health Status', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('../reports/visuals/inventory_status.png', dpi=150)
plt.close()

print("Exploratory Data Analysis completed. Visualizations saved successfully in reports/visuals/.")
