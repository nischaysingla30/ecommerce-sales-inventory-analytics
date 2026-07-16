# E-Commerce Sales & Inventory Analytics Project

A complete, end-to-end Data Analyst portfolio project demonstrating **SQL**, **Python (Pandas, NumPy, Matplotlib)**, **Excel**, and **Power BI** skills. 

This project simulates a real-world business scenario where a data analyst cleans raw transactional data, runs advanced SQL databases diagnostic queries, designs an interactive KPI spreadsheet, and builds a multi-page interactive executive Power BI dashboard.

---

## 📂 Repository Structure

The project files are organized as follows:

```
ecommerce_sales_inventory_analytics/
├── data/
│   ├── raw/                       # Raw synthetic CSV files with anomalies (generated)
│   └── processed/                 # Cleaned CSV files ready for SQL/Power BI import
├── python/
│   ├── generate_data.py           # Script that generates raw data (100,000+ transaction rows)
│   ├── data_cleaning.py           # Script to clean raw data, handle nulls, duplicates, outliers
│   └── eda.py                     # Script running Exploratory Data Analysis & plotting trends
├── sql/
│   ├── schema.sql                 # DDL schema definition script (PK, FK, Views)
│   └── queries.sql                # SQL analytical queries (CTEs, Window functions, Joins)
├── excel/
│   └── generate_excel.py          # Python compiler building a stylized Excel KPI workbook
├── power_bi/
│   ├── dax_measures.dax           # Calculated DAX measures for KPI visualization
│   └── model_schema.md            # Data modeling instructions & dashboard layouts
├── reports/
│   ├── ECommerce_Sales_Inventory_Diagnostics.xlsx  # Styled Excel Workbook with formulas
│   └── visuals/                   # EDA visual outputs (Monthly Sales, Ranks, Inventory Health)
└── README.md                      # Main project documentation (Objectives, Workflow, Insights)
```

---

## 🎯 Project Objectives & Business Metrics

The goal of this project is to assist an e-commerce retailer in maximizing margins, understanding customer profiles, and optimizing inventory management. The key business metrics analyzed are:

* **Sales Metrics**: Gross Revenue, Discount impact, Net Sales, Average Order Value (AOV), and Month-over-Month (MoM) Growth.
* **Profitability Metrics**: Cost of Goods Sold (COGS), Net Profit, and Profit Margin % across regions, categories, and customer segments.
* **Customer Metrics**: Segment and regional distribution, and Customer Lifetime Value (CLV) cohorts.
* **Operational Metrics**: Return Rate % by product category, current stock levels vs. reorder points, and warehouse restock warnings.

---

## 📊 Dataset Schema (Star Schema)

The database consists of **6 related tables** modeling a typical retail business transactional structure:

1. **Customers**: 5,000 unique records (Name, Email, Age, Gender, Segment, Region, Signup Date).
2. **Categories**: 5 product classes (Electronics, Home & Kitchen, Clothing, Beauty & Personal Care, Sports & Outdoors).
3. **Products**: 100 products mapping to categories with Cost Price and Retail Price.
4. **Orders**: 60,000 sales transactions (Order Date, Shipping Method, Status, Region).
5. **Order_Items**: 105,172 item-level transaction records (Quantity, Discount %, Return Status).
6. **Inventory**: 100 stock level records indicating warehouse locations and reorder points.

### Relationships Definition:
* `Customers (1)` ➔ `Orders (*)`
* `Orders (1)` ➔ `Order_Items (*)`
* `Products (1)` ➔ `Order_Items (*)`
* `Categories (1)` ➔ `Products (*)`
* `Products (1)` ➔ `Inventory (1)`

---

## 🚀 Workflow & Implementation Details

### Step 1: Python Data Engineering (Data Gen & Cleaning)
* **Synthetic Data Generation (`python/generate_data.py`)**: Generated over 105,000 item-level rows covering a 2-year calendar period. Incorporated realistic business logic such as high-sales seasonality in winter (Nov-Dec) and regional customer clusters. Injected data anomalies: missing genders and age fields, age outliers (negative and >100 values), exact duplicate order item lines, and extreme quantity/discount outliers.
* **Data Cleaning (`python/data_cleaning.py`)**: Deduplicated rows, imputed missing genders to "Not Specified" and missing ages to the median, capped quantity and discount outliers to realistic values (e.g. capping quantity >10 at the median, and capping discount >50% at 30%), enforced datatypes, and verified referential integrity.
* **Exploratory Data Analysis (`python/eda.py`)**: Produced business charts showing Monthly Net Revenue trends, Category Revenue & Margins, Regional segment sales, and Inventory health status.

### Step 2: Advanced SQL Databases Analysis (`sql/`)
* **`schema.sql`**: Created the relational DDL schemas with primary, foreign keys, CHECK constraints, and built a relational **View** (`v_order_details`) consolidating transactions to speed up reporting.
* **`queries.sql`**: Designed analytical queries resolving critical business questions:
  * **CTEs & Window Functions**: Top 3 products sold per category based on revenue using `DENSE_RANK()`.
  * **Time Series Analysis**: Month-over-Month revenue growth and daily running total revenue using `LAG()` and cumulative window sums.
  * **Customer Cohorts**: Purchase frequency segmentation showing how many customers are repeat buyers.
  * **Inventory Alerts**: Warning triggers flagging items when `stock_level <= reorder_point`.

### Step 3: Excel Dashboard & Formula Diagnostics (`excel/`)
Compiled a corporate-styled, multi-sheet workbook (`reports/ECommerce_Sales_Inventory_Diagnostics.xlsx`):
* **Calculated Columns**: Reconstructed retail prices, cost prices, net revenue, margins, and profit fields inside the transactional sheet using dynamic **Excel Formulas** (`XLOOKUP`, `SUM`, `IF`, `AVERAGE`).
* **KPI Dashboard Sheet**: Highlighted executive summaries:
  * High-level cards summarizing Net Sales, Cost, Profit, Margin, and Return Rates.
  * Product Category Breakdowns utilizing `SUMIFS` referencing category sheets.
  * Regional Performance summaries mapping sales, count of orders, average order values, and cancellation counts using `COUNTIFS` and `SUMIFS`.
  * Formatted with Segoe UI typography and a corporate Dark Navy theme.

### Step 4: Power BI Visualization & Modeling (`power_bi/`)
* **Model Schema**: Modeled raw tables inside a **Star Schema** with a dedicated generated `Calendar` table.
* **DAX Measures**: Formulated measures for advanced calculations:
  * Transactional totals (`Total Sales`, `Total Cost`, `Total Profit`, `Profit Margin %`).
  * Operational alerts (`Return Rate %`, `Reorder Point Alert Count`).
  * Time intelligence metrics (`Sales PY` [Previous Year], `Sales PM` [Previous Month], `YoY Sales Growth %`, `MoM Sales Growth %`).

---

## 📈 Key Business Insights & Recommendations

Based on Python EDA and SQL queries, here are the core findings:

1. **Winter Seasonality Spikes**: Data confirms massive sales surges in November and December, representing over 25% of annual net revenue due to holiday seasons. 
   * *Recommendation*: Warehouse managers should initiate restock cycles in early September, and marketing campaigns should prioritize high-margin electronics during winter peaks.
2. **Profit Margins by Category**: **Electronics** generates the highest total net revenue, but **Beauty & Personal Care** exhibits the highest net profit margins (approaching 54%).
   * *Recommendation*: Allocate larger digital marketing budgets to Beauty products to increase overall company margins.
3. **Regional Performance**: The **East** and **West** regions are the largest sales drivers, contributing ~65% of net sales, with the Corporate customer segment representing the highest AOV ($210.00).
   * *Recommendation*: Bundle smaller Consumer items with premium corporate electronics to cross-sell to high-value customers.
4. **Operational Efficiencies (Returns)**: **Clothing** has the highest return rates (~6.2%), indicating fit or description mismatch.
   * *Recommendation*: Implement virtual sizing tools on the front-end to decrease returns.
5. **Inventory Alert Status**: Currently, **22%** of products are flagged with "Restock Alert" (stock level at or below the reorder threshold).
   * *Recommendation*: Set up automated reorder emails linking the Excel Inventory sheet directly to suppliers to prevent stock-outs.

---

## 🛠️ How to Run the Code

### Prerequisites
* Python 3.10+
* Required packages: `pandas`, `numpy`, `matplotlib`, `openpyxl`

### Step-by-Step Instructions
1. Clone this repository.
2. Navigate to the `python` directory and generate the synthetic raw dataset:
   ```bash
   python generate_data.py
   ```
3. Run the data cleaning script to preprocess raw CSVs:
   ```bash
   python data_cleaning.py
   ```
4. Generate the analytical charts:
   ```bash
   python eda.py
   ```
5. Build the styled Excel diagnostics sheet:
   ```bash
   python ../excel/generate_excel.py
   ```
6. Load the cleaned CSV files from `data/processed/` into your database of choice (e.g. SQLite, PostgreSQL) and run `sql/queries.sql` to verify database analytics.
7. Open Power BI, import the processed CSV files, and utilize `power_bi/model_schema.md` and `power_bi/dax_measures.dax` to assemble the interactive dashboards.
 
