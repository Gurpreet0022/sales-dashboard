--Project: E-commerce Sales Analysis Dashboard with SQL + Streamlit

-- File 1: database_setup.sql (SQLite compatible)
-- This script sets up the sample e-commerce database for SQLite
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    gender TEXT,
    country TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Populate with sample data
INSERT INTO customers (name, email, gender, country) VALUES
('Alice', 'alice@example.com', 'Female', 'India'),
('Bob', 'bob@example.com', 'Male', 'USA'),
('Charlie', 'charlie@example.com', 'Male', 'UK');

INSERT INTO products (product_name, category, price) VALUES
('Laptop', 'Electronics', 70000),
('Headphones', 'Electronics', 2000),
('Notebook', 'Stationery', 100);

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2024-06-01'),
(2, 2, 2, '2024-06-03'),
(3, 3, 10, '2024-06-05');
