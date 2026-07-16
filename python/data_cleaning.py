import os
import pandas as pd
import numpy as np

# Create processed data folder
os.makedirs('../data/processed', exist_ok=True)

print("Starting data cleaning process...")

# -----------------------------------------------------------------------------
# 1. LOAD DATA
# -----------------------------------------------------------------------------
try:
    df_categories = pd.read_csv('../data/raw/categories.csv')
    df_products = pd.read_csv('../data/raw/products.csv')
    df_customers = pd.read_csv('../data/raw/customers.csv')
    df_orders = pd.read_csv('../data/raw/orders.csv')
    df_order_items = pd.read_csv('../data/raw/order_items.csv')
    df_inventory = pd.read_csv('../data/raw/inventory.csv')
    print("Successfully loaded all raw tables.")
except FileNotFoundError as e:
    print(f"Error loading files. Ensure generate_data.py has run successfully. Details: {e}")
    exit(1)

# -----------------------------------------------------------------------------
# 2. CLEAN CUSTOMERS
# -----------------------------------------------------------------------------
print("Cleaning Customers...")

# Handle duplicate customer rows (if any)
df_customers = df_customers.drop_duplicates(subset=['customer_id'])

# Handle missing gender
df_customers['gender'] = df_customers['gender'].fillna('Not Specified')

# Handle age outliers & missing values
# Outliers: age < 18 or age > 100 or null
median_age = int(df_customers[(df_customers['age'] >= 18) & (df_customers['age'] <= 100)]['age'].median())
df_customers['age'] = df_customers['age'].apply(lambda x: median_age if pd.isna(x) or x < 18 or x > 100 else int(x))

# Handle missing signup dates - fill with median or default to min signup date
min_signup = df_customers['signup_date'].dropna().min()
df_customers['signup_date'] = df_customers['signup_date'].fillna(min_signup)

# Ensure data types
df_customers['customer_id'] = df_customers['customer_id'].astype(int)
df_customers['age'] = df_customers['age'].astype(int)

# -----------------------------------------------------------------------------
# 3. CLEAN PRODUCTS & CATEGORIES
# -----------------------------------------------------------------------------
print("Cleaning Products & Categories...")
df_categories = df_categories.drop_duplicates()
df_products = df_products.drop_duplicates(subset=['product_id'])

# Ensure prices are positive and numeric
df_products['cost_price'] = pd.to_numeric(df_products['cost_price'], errors='coerce')
df_products['retail_price'] = pd.to_numeric(df_products['retail_price'], errors='coerce')
# Check if cost > retail (margins should be positive)
df_products['retail_price'] = np.where(df_products['retail_price'] <= df_products['cost_price'], 
                                       df_products['cost_price'] * 1.5, 
                                       df_products['retail_price'])

# -----------------------------------------------------------------------------
# 4. CLEAN ORDERS
# -----------------------------------------------------------------------------
print("Cleaning Orders...")
df_orders = df_orders.drop_duplicates(subset=['order_id'])
df_orders['order_date'] = pd.to_datetime(df_orders['order_date'], errors='coerce')

# Check if any orders have missing dates and fill with a fallback
default_order_date = pd.to_datetime('2024-01-01')
df_orders['order_date'] = df_orders['order_date'].fillna(default_order_date)

# Ensure shipping method is standard-cased
df_orders['shipping_method'] = df_orders['shipping_method'].fillna('Standard')
df_orders['status'] = df_orders['status'].fillna('Shipped')

# Format dates to string YYYY-MM-DD
df_orders['order_date'] = df_orders['order_date'].dt.strftime('%Y-%m-%d')

# -----------------------------------------------------------------------------
# 5. CLEAN ORDER ITEMS
# -----------------------------------------------------------------------------
print("Cleaning Order Items...")

# Remove exact duplicates
initial_len = len(df_order_items)
df_order_items = df_order_items.drop_duplicates()
print(f"Removed {initial_len - len(df_order_items)} duplicate order item rows.")

# Handle quantity outliers (e.g. negative values, huge values)
# Clean negative quantities by taking absolute value, and default to 1 if 0
df_order_items['quantity'] = df_order_items['quantity'].apply(lambda x: abs(x) if x < 0 else x)
df_order_items['quantity'] = df_order_items['quantity'].replace(0, 1)

# Cap quantity at 10 (outliers like 120 are capped at median/reasonable max)
median_qty = int(df_order_items[df_order_items['quantity'] <= 10]['quantity'].median())
df_order_items['quantity'] = df_order_items['quantity'].apply(lambda x: median_qty if x > 10 else x)

# Handle discount anomalies (null values and high outliers > 50%)
df_order_items['discount_pct'] = df_order_items['discount_pct'].fillna(0.0)
df_order_items['discount_pct'] = df_order_items['discount_pct'].apply(lambda x: 0.30 if x > 0.50 else x)

# Ensure return status is 0 or 1
df_order_items['return_status'] = df_order_items['return_status'].fillna(0).astype(int)

# -----------------------------------------------------------------------------
# 6. CLEAN INVENTORY
# -----------------------------------------------------------------------------
print("Cleaning Inventory...")
df_inventory = df_inventory.drop_duplicates(subset=['product_id'])
df_inventory['stock_level'] = df_inventory['stock_level'].apply(lambda x: max(0, x))
df_inventory['reorder_point'] = df_inventory['reorder_point'].apply(lambda x: max(0, x))

# -----------------------------------------------------------------------------
# 7. REFERENTIAL INTEGRITY CHECKS
# -----------------------------------------------------------------------------
print("Running referential integrity checks...")

# Keep only order items that correspond to valid orders & products
valid_orders = df_orders['order_id'].unique()
valid_products = df_products['product_id'].unique()

df_order_items = df_order_items[
    df_order_items['order_id'].isin(valid_orders) & 
    df_order_items['product_id'].isin(valid_products)
]

# Keep only orders that correspond to valid customers
valid_customers = df_customers['customer_id'].unique()
df_orders = df_orders[df_orders['customer_id'].isin(valid_customers)]

# -----------------------------------------------------------------------------
# 8. EXPORT CLEANED DATA
# -----------------------------------------------------------------------------
print("Exporting cleaned data to CSV...")

df_categories.to_csv('../data/processed/categories.csv', index=False)
df_products.to_csv('../data/processed/products.csv', index=False)
df_customers.to_csv('../data/processed/customers.csv', index=False)
df_orders.to_csv('../data/processed/orders.csv', index=False)
df_order_items.to_csv('../data/processed/order_items.csv', index=False)
df_inventory.to_csv('../data/processed/inventory.csv', index=False)

print(f"Data cleaning completed successfully. Cleaned records count:")
print(f"Categories: {len(df_categories)}")
print(f"Products: {len(df_products)}")
print(f"Customers: {len(df_customers)}")
print(f"Orders: {len(df_orders)}")
print(f"Order Items: {len(df_order_items)}")
print(f"Inventory: {len(df_inventory)}")
