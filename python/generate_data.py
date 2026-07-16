import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Create raw data folder
os.makedirs('../data/raw', exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

print("Starting synthetic data generation...")

# -----------------------------------------------------------------------------
# 1. CATEGORIES & PRODUCTS
# -----------------------------------------------------------------------------
categories_data = {
    "category_id": [1, 2, 3, 4, 5],
    "category_name": ["Electronics", "Home & Kitchen", "Clothing", "Beauty & Personal Care", "Sports & Outdoors"]
}
df_categories = pd.DataFrame(categories_data)
df_categories.to_csv('../data/raw/categories.csv', index=False)
print("Generated Categories table.")

# Product templates per category
product_templates = {
    1: [("Smart Watch", 120, 249), ("Wireless Earbuds", 45, 99), ("Bluetooth Speaker", 30, 79), 
        ("Laptop Stand", 15, 39), ("USB-C Hub", 12, 29), ("Phone Charger", 5, 15), 
        ("Gaming Mouse", 25, 59), ("Mechanical Keyboard", 50, 119), ("Monitor Lightbar", 35, 79), 
        ("Tablet Sleeve", 10, 25), ("Noise Cancelling Headphones", 150, 299), ("Wireless Charger", 18, 39),
        ("Smartphone Tripod", 14, 30), ("External SSD 1TB", 70, 149), ("Webcam 1080p", 40, 89), 
        ("Gaming Headset", 45, 99), ("Smart Plug Pack", 15, 35), ("Stylus Pen", 20, 49), 
        ("E-Reader", 65, 129), ("Graphics Tablet", 80, 179)],
    2: [("Chef's Knife", 28, 69), ("Coffee Grinder", 20, 49), ("Electric Kettle", 22, 59), 
        ("Non-Stick Frypan", 18, 45), ("Air Fryer", 55, 120), ("Blender 600W", 35, 79), 
        ("Food Container Set", 12, 29), ("Silicone Spatulas", 4, 12), ("Digital Kitchen Scale", 8, 20), 
        ("Toaster 2-Slice", 15, 35), ("French Press", 12, 29), ("Stainless Steel Kettle", 18, 39),
        ("Knife Sharpening Stone", 10, 25), ("Cutting Board Set", 15, 35), ("Electric Milk Frother", 7, 19), 
        ("Vacuum Sealer", 40, 89), ("Waffle Maker", 22, 49), ("Slow Cooker", 30, 69), 
        ("Garlic Press", 5, 15), ("Salad Spinner", 10, 24)],
    3: [("Cotton T-Shirt", 6, 18), ("Denim Jeans", 18, 49), ("Hoodie Sweatshirt", 15, 39), 
        ("Running Socks 3-Pack", 3, 12), ("Athletic Shorts", 8, 22), ("Canvas Sneakers", 12, 35), 
        ("Leather Belt", 10, 28), ("Sunglasses", 15, 45), ("Winter Beanie", 4, 15), 
        ("Rain Jacket", 25, 69), ("V-Neck Sweater", 14, 35), ("Chino Pants", 16, 42),
        ("Activewear Leggings", 11, 29), ("Pajama Set", 12, 32), ("Swim Trunk", 9, 25), 
        ("Cargo Shorts", 13, 30), ("Puffer Vest", 22, 55), ("Leather Gloves", 12, 35), 
        ("Baseball Cap", 5, 18), ("Flannel Shirt", 11, 29)],
    4: [("Face Moisturizer", 10, 25), ("Hyaluronic Acid Serum", 12, 28), ("Sunscreen SPF 50", 8, 19), 
        ("Lip Balm Pack", 2, 8), ("Exfoliating Scrub", 7, 18), ("Scented Candle", 6, 18), 
        ("Hair Dryer 1800W", 20, 49), ("Hair Straightener", 25, 59), ("Makeup Brush Set", 9, 25), 
        ("Matte Lipstick", 6, 16), ("Clay Mask", 8, 22), ("Hydrating Toner", 9, 24),
        ("Shampoo & Conditioner Set", 12, 30), ("Argan Hair Oil", 10, 26), ("Electric Toothbrush", 30, 79), 
        ("Water Flosser", 24, 59), ("Body Wash 33oz", 7, 18), ("Mascara Black", 5, 14), 
        ("Eyeshadow Palette", 12, 32), ("Nail Polish Set", 8, 20)],
    5: [("Yoga Mat 6mm", 8, 22), ("Dumbbell Set 20lbs", 25, 59), ("Resistance Bands", 5, 15), 
        ("Water Bottle 32oz", 6, 18), ("Microfiber Towel", 3, 10), ("Running Backpack", 18, 45), 
        ("Sleeping Bag", 22, 59), ("Camping Tent 2-Person", 45, 110), ("Trekking Poles", 16, 39), 
        ("Bicycle Helmet", 18, 45), ("Foam Roller", 7, 19), ("Jump Rope", 4, 12),
        ("Camping Stove", 15, 35), ("Hammock Double", 12, 29), ("Golf Balls 12-Pack", 10, 25), 
        ("Tennis Racket", 30, 75), ("Swim Goggles", 6, 16), ("Ankle Weights", 8, 20), 
        ("Adjustable Hand Gripper", 4, 10), ("Dry Bag 20L", 9, 22)]
}

products = []
product_id = 1
for cat_id, templates in product_templates.items():
    for name, cost, retail in templates:
        products.append({
            "product_id": product_id,
            "product_name": name,
            "category_id": cat_id,
            "cost_price": cost,
            "retail_price": retail
        })
        product_id += 1

df_products = pd.DataFrame(products)
df_products.to_csv('../data/raw/products.csv', index=False)
print(f"Generated Products table with {len(df_products)} products.")


# -----------------------------------------------------------------------------
# 2. CUSTOMERS
# -----------------------------------------------------------------------------
num_customers = 5000
first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "James", "Jessica", "Robert", "Karen",
               "William", "Lisa", "Joseph", "Betty", "Thomas", "Sandra", "Daniel", "Donna", "Matthew", "Carol",
               "Mark", "Ruth", "Donald", "Michelle", "Steven", "Laura", "Paul", "Kimberly", "Andrew", "Elizabeth",
               "Joshua", "Melissa", "Kenneth", "Amy", "Kevin", "Mary", "Brian", "Angela", "George", "Brenda",
               "Edward", "Nicole", "Ronald", "Gary", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
              "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
              "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
              "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]

customer_segments = ["Consumer", "Corporate", "Home Office"]
regions = ["East", "West", "South", "Midwest"]

customers = []
start_date = datetime(2023, 1, 1)

for cid in range(1, num_customers + 1):
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)
    name = f"{f_name} {l_name}"
    email = f"{f_name.lower()}.{l_name.lower()}{random.randint(10, 99)}@example.com"
    
    # Introduce null values in gender & age (approx 5-10% missing)
    gender = random.choice(["Male", "Female"]) if random.random() > 0.08 else None
    
    # Introduce outliers in age (negative, extremely high, or null)
    age_rand = random.random()
    if age_rand < 0.06:
        age = None
    elif age_rand < 0.08:
        age = random.choice([-5, -12, 140, 150]) # Outliers
    else:
        age = random.randint(18, 75)
        
    segment = np.random.choice(customer_segments, p=[0.60, 0.25, 0.15])
    region = np.random.choice(regions, p=[0.35, 0.30, 0.20, 0.15])
    
    # Introduce null signup date (approx 3%)
    if random.random() > 0.03:
        signup_days = random.randint(0, 365)
        signup_date = (start_date + timedelta(days=signup_days)).strftime("%Y-%m-%d")
    else:
        signup_date = None

    customers.append({
        "customer_id": cid,
        "customer_name": name,
        "email": email,
        "gender": gender,
        "age": age,
        "customer_segment": segment,
        "region": region,
        "signup_date": signup_date
    })

df_customers = pd.DataFrame(customers)
df_customers.to_csv('../data/raw/customers.csv', index=False)
print(f"Generated Customers table with {len(df_customers)} records.")


# -----------------------------------------------------------------------------
# 3. ORDERS & ORDER ITEMS
# -----------------------------------------------------------------------------
num_orders = 60000
orders = []
order_items = []

order_statuses = ["Delivered", "Shipped", "Cancelled", "Returned"]
shipping_methods = ["Standard", "Second Day", "Same Day"]

# Date generation setup (Jan 1, 2024 to Dec 31, 2025)
base_start = datetime(2024, 1, 1)
base_end = datetime(2025, 12, 31)
total_days = (base_end - base_start).days

order_item_id = 1
print("Generating Orders & Order Items...")

for oid in range(1, num_orders + 1):
    cust_id = random.randint(1, num_customers)
    cust_info = customers[cust_id - 1]
    
    # Determine order date with seasonality (peak in Nov-Dec, spike in high-summer, lower in early year)
    rand_day = random.randint(0, total_days)
    order_dt = base_start + timedelta(days=rand_day)
    
    # Seasonality weights: increase chance of shopping in November, December, or mid-year
    month = order_dt.month
    if month in [11, 12]:
        # High sales in winter: extra orders generated or date shifted slightly
        if random.random() < 0.3:
            order_dt = order_dt + timedelta(days=random.randint(-15, 15))
            # clamp dates
            order_dt = max(base_start, min(order_dt, base_end))
    
    # Select Shipping Method (weight standard higher)
    ship_method = np.random.choice(shipping_methods, p=[0.70, 0.20, 0.10])
    
    # Order Status distribution (mostly Delivered or Shipped, some Cancelled/Returned)
    status = np.random.choice(order_statuses, p=[0.82, 0.10, 0.05, 0.03])
    
    # Match region to customer region
    region = cust_info["region"]
    
    orders.append({
        "order_id": oid,
        "customer_id": cust_id,
        "order_date": order_dt.strftime("%Y-%m-%d"),
        "shipping_method": ship_method,
        "status": status,
        "region": region
    })
    
    # Generate items for this order (1 to 5 items)
    num_items = np.random.choice([1, 2, 3, 4, 5], p=[0.55, 0.25, 0.12, 0.06, 0.02])
    
    # Keep track of products in this order to avoid immediate duplicate combinations unless forced
    products_in_order = set()
    
    for _ in range(num_items):
        prod = random.choice(products)
        p_id = prod["product_id"]
        
        # Quantity distributions (normally 1-5, with outliers)
        q_rand = random.random()
        if q_rand < 0.005:
            qty = -2  # Outlier
        elif q_rand < 0.01:
            qty = 120  # Outlier
        else:
            qty = random.randint(1, 4)
            
        # Discount percent (0% to 30%, sometimes null or high outlier)
        d_rand = random.random()
        if d_rand < 0.05:
            discount = None  # Missing values representation
        elif d_rand < 0.06:
            discount = 0.85  # Outlier (85% discount)
        elif d_rand < 0.40:
            # Standard discounts
            discount = round(random.choice([0.05, 0.10, 0.15, 0.20, 0.25, 0.30]), 2)
        else:
            discount = 0.0
            
        # If order status is Returned, match item return status
        item_returned = 1 if status == "Returned" else 0
        # Sometimes an individual item can be returned even if order status is Delivered
        if status == "Delivered" and random.random() < 0.02:
            item_returned = 1
            
        order_items.append({
            "order_item_id": order_item_id,
            "order_id": oid,
            "product_id": p_id,
            "quantity": qty,
            "discount_pct": discount,
            "return_status": item_returned
        })
        order_item_id += 1
        
        # Inject occasional duplicate rows (exact duplicate order items)
        if random.random() < 0.001:  # 0.1% chance of exact duplicate row
            order_items.append({
                "order_item_id": order_item_id - 1,
                "order_id": oid,
                "product_id": p_id,
                "quantity": qty,
                "discount_pct": discount,
                "return_status": item_returned
            })

df_orders = pd.DataFrame(orders)
df_orders.to_csv('../data/raw/orders.csv', index=False)

df_order_items = pd.DataFrame(order_items)
df_order_items.to_csv('../data/raw/order_items.csv', index=False)

print(f"Generated Orders table with {len(df_orders)} records.")
print(f"Generated Order Items table with {len(df_order_items)} records (including duplicates/anomalies).")


# -----------------------------------------------------------------------------
# 4. INVENTORY
# -----------------------------------------------------------------------------
inventory = []
inventory_id = 1
warehouses = {
    "East": "WH-East",
    "West": "WH-West",
    "South": "WH-South",
    "Midwest": "WH-Midwest"
}

for prod in products:
    p_id = prod["product_id"]
    # Get total sales for this product to set dynamic stock levels
    # (products that sell more have higher stock)
    base_popularity = random.randint(1, 5)
    
    # Establish stock level
    stock_level = random.randint(20, 200) * base_popularity
    # Reorder point (15% to 25% of stock level)
    reorder_point = max(10, int(stock_level * random.choice([0.15, 0.20, 0.25])))
    
    # Warehouse location based on random region
    wh_loc = warehouses[random.choice(regions)]
    
    inventory.append({
        "inventory_id": inventory_id,
        "product_id": p_id,
        "stock_level": stock_level,
        "reorder_point": reorder_point,
        "warehouse_location": wh_loc
    })
    inventory_id += 1

df_inventory = pd.DataFrame(inventory)
df_inventory.to_csv('../data/raw/inventory.csv', index=False)

print(f"Generated Inventory table with {len(df_inventory)} records.")
print("Synthetic raw data generation completed successfully!")
