-- E-Commerce Sales & Inventory Advanced Analytics Queries
-- Demonstrating: Joins, CTEs, Window Functions, Grouping, and Conditional Logic

-- =============================================================================
-- 1. EXECUTIVE SUMMARY KPI ANALYSIS
-- =============================================================================
-- Calculates total orders, total net revenue, cost, profit, and overall profit margin
-- Excluding cancelled and returned orders from active revenue/profit calculations
SELECT 
    COUNT(DISTINCT order_id) AS Total_Orders,
    SUM(net_revenue) AS Gross_Net_Revenue,
    SUM(total_cost) AS Total_Cost_of_Goods,
    SUM(profit) AS Net_Profit,
    ROUND((SUM(profit) / SUM(net_revenue)) * 100, 2) AS Profit_Margin_Pct,
    ROUND(AVG(discount_pct) * 100, 2) AS Avg_Discount_Pct
FROM v_order_details
WHERE order_status NOT IN ('Cancelled', 'Returned');


-- =============================================================================
-- 2. MONTH-OVER-MONTH (MoM) REVENUE & MOM GROWTH (CTEs & Window Functions)
-- =============================================================================
-- Steps:
--   1. Extract year/month from order_date and aggregate net revenue.
--   2. Use LAG() to fetch the previous month's revenue.
--   3. Compute MoM revenue growth rate.
WITH MonthlySales AS (
    SELECT 
        -- Date formatting syntax works in SQLite, PostgreSQL, and MySQL
        -- For SQLite/Postgres: strftime or DATE_TRUNC. Let's use standard string formatting.
        SUBSTR(order_date, 1, 7) AS Order_Month,
        SUM(net_revenue) AS Net_Revenue
    FROM v_order_details
    WHERE order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY SUBSTR(order_date, 1, 7)
),
MonthlySalesLag AS (
    SELECT 
        Order_Month,
        Net_Revenue,
        LAG(Net_Revenue, 1) OVER (ORDER BY Order_Month) AS Prev_Month_Revenue
    FROM MonthlySales
)
SELECT 
    Order_Month,
    ROUND(Net_Revenue, 2) AS Current_Month_Revenue,
    ROUND(Prev_Month_Revenue, 2) AS Previous_Month_Revenue,
    ROUND(Net_Revenue - Prev_Month_Revenue, 2) AS Monthly_Revenue_Change,
    ROUND(((Net_Revenue - Prev_Month_Revenue) / Prev_Month_Revenue) * 100, 2) AS MoM_Growth_Pct
FROM MonthlySalesLag;


-- =============================================================================
-- 3. CUMULATIVE RUNNING TOTAL REVENUE (Window Function)
-- =============================================================================
-- Tracks how revenue builds up cumulatively day by day
SELECT 
    order_date,
    ROUND(SUM(net_revenue), 2) AS Daily_Revenue,
    ROUND(SUM(SUM(net_revenue)) OVER (
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS Cumulative_Running_Revenue
FROM v_order_details
WHERE order_status NOT IN ('Cancelled', 'Returned')
GROUP BY order_date
ORDER BY order_date
LIMIT 30; -- Capped for display purposes


-- =============================================================================
-- 4. TOP 3 PRODUCTS BY REVENUE IN EACH CATEGORY (CTEs & DENSE_RANK)
-- =============================================================================
-- Uses DENSE_RANK() window function to identify the top products per category
WITH ProductRankings AS (
    SELECT 
        category_name,
        product_name,
        SUM(net_revenue) AS Total_Product_Revenue,
        DENSE_RANK() OVER (
            PARTITION BY category_name 
            ORDER BY SUM(net_revenue) DESC
        ) AS Product_Rank
    FROM v_order_details
    WHERE order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY category_name, product_name
)
SELECT 
    category_name,
    product_name,
    ROUND(Total_Product_Revenue, 2) AS Revenue,
    Product_Rank
FROM ProductRankings
WHERE Product_Rank <= 3
ORDER BY category_name, Product_Rank;


-- =============================================================================
-- 5. REGIONAL PERFORMANCE & KEY METRICS (Joins & Aggregations)
-- =============================================================================
-- Evaluates the business distribution across East, West, South, and Midwest regions
SELECT 
    customer_region AS Region,
    COUNT(DISTINCT order_id) AS Total_Orders,
    SUM(quantity) AS Total_Units_Sold,
    ROUND(SUM(net_revenue), 2) AS Net_Sales,
    ROUND(SUM(profit), 2) AS Net_Profit,
    ROUND((SUM(net_revenue) / COUNT(DISTINCT order_id)), 2) AS Average_Order_Value,
    ROUND((SUM(profit) / SUM(net_revenue)) * 100, 2) AS Profit_Margin_Pct
FROM v_order_details
WHERE order_status NOT IN ('Cancelled', 'Returned')
GROUP BY customer_region
ORDER BY Net_Sales DESC;


-- =============================================================================
-- 6. PRODUCT RETURN AND CANCELLATION ANALYSIS (Conditional Aggregation)
-- =============================================================================
-- Understands return rate metrics by product category to optimize product quality
SELECT 
    category_name,
    COUNT(order_item_id) AS Total_Items_Ordered,
    SUM(CASE WHEN return_status = 1 THEN 1 ELSE 0 END) AS Items_Returned,
    ROUND(
        (SUM(CASE WHEN return_status = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(order_item_id), 
        2
    ) AS Return_Rate_Pct
FROM v_order_details
GROUP BY category_name
ORDER BY Return_Rate_Pct DESC;


-- =============================================================================
-- 7. REPEAT CUSTOMER ANALYSIS (CTE & COUNT)
-- =============================================================================
-- Calculates purchase frequency distribution: how many customers bought once, twice, etc.
WITH CustomerPurchaseCount AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS Order_Frequency
    FROM Orders
    WHERE status NOT IN ('Cancelled')
    GROUP BY customer_id
)
SELECT 
    Order_Frequency AS Purchases_Made,
    COUNT(customer_id) AS Customer_Count,
    ROUND((COUNT(customer_id) * 100.0) / (SELECT COUNT(*) FROM Customers), 2) AS Pct_of_Total_Customers
FROM CustomerPurchaseCount
GROUP BY Order_Frequency
ORDER BY Purchases_Made;


-- =============================================================================
-- 8. INVENTORY REORDER ALERTS (Inventory Joins)
-- =============================================================================
-- Generates stock alerts when current stock drops below the reorder point
-- Joins Inventory table with Products and Categories to identify items and vendors
SELECT 
    i.inventory_id,
    p.product_name,
    c.category_name,
    i.stock_level,
    i.reorder_point,
    i.warehouse_location,
    CASE 
        WHEN i.stock_level = 0 THEN 'OUT OF STOCK'
        WHEN i.stock_level <= i.reorder_point THEN 'REORDER IMMEDIATE'
        ELSE 'STOCKED'
    END AS Stock_Status
FROM Inventory i
JOIN Products p ON i.product_id = p.product_id
JOIN Categories c ON p.category_id = c.category_id
WHERE i.stock_level <= i.reorder_point
ORDER BY i.stock_level ASC;
