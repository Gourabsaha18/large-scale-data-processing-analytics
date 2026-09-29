-- Total Revenue
SELECT ROUND(SUM(Revenue), 2) AS total_revenue
FROM sales;

-- Revenue by Category
SELECT
    Category,
    ROUND(SUM(Revenue), 2) AS revenue
FROM sales
GROUP BY Category
ORDER BY revenue DESC;

-- Revenue by Region
SELECT
    Region,
    ROUND(SUM(Revenue), 2) AS revenue
FROM sales
GROUP BY Region
ORDER BY revenue DESC;

-- Monthly Revenue
SELECT
    Year,
    Month,
    ROUND(SUM(Revenue), 2) AS revenue
FROM sales
GROUP BY Year, Month
ORDER BY Year, Month;

-- Top 10 Products
SELECT
    Product_Name,
    ROUND(SUM(Revenue), 2) AS revenue
FROM sales
GROUP BY Product_Name
ORDER BY revenue DESC
LIMIT 10;

-- Average Order Value (if Order_ID exists)
SELECT
    ROUND(SUM(Revenue) / COUNT(DISTINCT Order_ID), 2) AS average_order_value
FROM sales;
