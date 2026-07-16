-- E-Commerce Sales & Inventory Analytics Schema Setup
-- Database: Suitable for PostgreSQL, SQLite, MySQL, or MS SQL Server

-- Drop tables if they exist (for easy re-running)
DROP TABLE IF EXISTS Inventory;
DROP TABLE IF EXISTS Order_Items;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Categories;

-- 1. CATEGORIES TABLE
CREATE TABLE Categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- 2. PRODUCTS TABLE
CREATE TABLE Products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL CHECK (cost_price >= 0),
    retail_price DECIMAL(10, 2) NOT NULL CHECK (retail_price >= cost_price),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- 3. CUSTOMERS TABLE
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    age INT CHECK (age >= 18 AND age <= 120),
    customer_segment VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    signup_date DATE NOT NULL
);

-- 4. ORDERS TABLE
CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    shipping_method VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- 5. ORDER_ITEMS TABLE
CREATE TABLE Order_Items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    discount_pct DECIMAL(5, 2) DEFAULT 0.00 CHECK (discount_pct >= 0.00 AND discount_pct <= 1.00),
    return_status INT DEFAULT 0 CHECK (return_status IN (0, 1)),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

-- 6. INVENTORY TABLE
CREATE TABLE Inventory (
    inventory_id INT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    stock_level INT NOT NULL CHECK (stock_level >= 0),
    reorder_point INT NOT NULL CHECK (reorder_point >= 0),
    warehouse_location VARCHAR(100) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

-- 7. ANALYSIS REPORTING VIEW
-- Pre-calculates revenue, discounts, net sales, and margins to simplify reporting queries.
CREATE VIEW v_order_details AS
SELECT 
    oi.order_item_id,
    o.order_id,
    o.order_date,
    o.status AS order_status,
    o.shipping_method,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.region AS customer_region,
    p.product_id,
    p.product_name,
    cat.category_name,
    oi.quantity,
    p.cost_price,
    p.retail_price,
    oi.discount_pct,
    (oi.quantity * p.retail_price) AS gross_revenue,
    (oi.quantity * p.retail_price * oi.discount_pct) AS discount_amount,
    (oi.quantity * p.retail_price * (1 - oi.discount_pct)) AS net_revenue,
    (oi.quantity * p.cost_price) AS total_cost,
    -- If returned, set net revenue to 0, profit becomes negative of the cost incurred
    CASE 
        WHEN oi.return_status = 1 THEN -(oi.quantity * p.cost_price)
        ELSE (oi.quantity * p.retail_price * (1 - oi.discount_pct)) - (oi.quantity * p.cost_price)
    END AS profit,
    oi.return_status
FROM Order_Items oi
JOIN Orders o ON oi.order_id = o.order_id
JOIN Customers c ON o.customer_id = c.customer_id
JOIN Products p ON oi.product_id = p.product_id
JOIN Categories cat ON p.category_id = cat.category_id;
