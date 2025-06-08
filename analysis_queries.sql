-- File 3: analysis_queries.sql
-- Useful SQL queries for data analysis

-- 1. Total sales revenue
SELECT SUM(p.price * o.quantity) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- 2. Top 5 selling products by quantity
SELECT p.product_name, SUM(o.quantity) AS total_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 5;

-- 3. Monthly revenue trend
SELECT strftime('%Y-%m', order_date) AS month, 
       SUM(p.price * o.quantity) AS monthly_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY month
ORDER BY month;

-- 4. Revenue by country
SELECT c.country, SUM(p.price * o.quantity) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.country
ORDER BY revenue DESC;

-- 5. Most active customers
SELECT c.name, COUNT(o.order_id) AS total_orders, 
       SUM(p.price * o.quantity) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 5;
