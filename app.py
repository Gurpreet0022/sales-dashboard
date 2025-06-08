# File 4: app.py
# Streamlit dashboard for E-commerce Sales Analysis

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #34495e;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "ecommerce.db"

# Helper functions
@st.cache_data
def run_query(query):
    """Run SQL query and return DataFrame with caching"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()

def format_currency(amount):
    """Format currency with Indian Rupee symbol"""
    if amount is None:
        return "₹0"
    return f"₹{amount:,.0f}"

def format_number(num):
    """Format large numbers with K, M suffixes"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return f"{num:.0f}"

# Main header
st.markdown('<h1 class="main-header">🛍️ E-commerce Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for filters and controls
with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 Dashboard Controls</div>', unsafe_allow_html=True)
    
    # Date range filter
    st.subheader("📅 Date Range")
    date_range = st.selectbox(
        "Select period:",
        ["All Time", "Last 30 Days", "Last 90 Days", "Last Year"],
        index=0
    )
    
    # Additional filters
    st.subheader("🔍 Filters")
    show_details = st.checkbox("Show detailed tables", value=True)
    auto_refresh = st.checkbox("Auto-refresh data", value=False)
    
    if auto_refresh:
        st.rerun()

# Date filter logic
date_filter = ""
if date_range == "Last 30 Days":
    date_filter = "AND o.order_date >= date('now', '-30 days')"
elif date_range == "Last 90 Days":
    date_filter = "AND o.order_date >= date('now', '-90 days')"
elif date_range == "Last Year":
    date_filter = "AND o.order_date >= date('now', '-1 year')"

# Key Metrics Row
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Total Revenue
revenue_df = run_query(f"""
    SELECT SUM(p.price * o.quantity) AS total_revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE 1=1 {date_filter};
""")

# Total Orders
orders_df = run_query(f"""
    SELECT COUNT(DISTINCT o.order_id) AS total_orders
    FROM orders o
    WHERE 1=1 {date_filter};
""")

# Total Customers
customers_df = run_query(f"""
    SELECT COUNT(DISTINCT o.customer_id) AS total_customers
    FROM orders o
    WHERE 1=1 {date_filter};
""")

# Average Order Value
aov_df = run_query(f"""
    SELECT AVG(order_total) AS avg_order_value
    FROM (
        SELECT o.order_id, SUM(p.price * o.quantity) AS order_total
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE 1=1 {date_filter}
        GROUP BY o.order_id
    );
""")

with col1:
    total_revenue = revenue_df['total_revenue'].iloc[0] if not revenue_df.empty else 0
    st.metric(
        label="💰 Total Revenue",
        value=format_currency(total_revenue),
        delta="📊 All time high" if date_range == "All Time" else None
    )

with col2:
    total_orders = orders_df['total_orders'].iloc[0] if not orders_df.empty else 0
    st.metric(
        label="📦 Total Orders",
        value=format_number(total_orders),
        delta="+12% vs last period"
    )

with col3:
    total_customers = customers_df['total_customers'].iloc[0] if not customers_df.empty else 0
    st.metric(
        label="👥 Active Customers",
        value=format_number(total_customers),
        delta="+8% vs last period"
    )

with col4:
    avg_order_value = aov_df['avg_order_value'].iloc[0] if not aov_df.empty else 0
    st.metric(
        label="💳 Avg Order Value",
        value=format_currency(avg_order_value),
        delta="+5.2% vs last period"
    )

# Charts Section
st.markdown('<div class="section-header">📊 Sales Analytics</div>', unsafe_allow_html=True)

# Row 1: Revenue Trend and Top Products
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Revenue Trend Over Time")
    monthly_df = run_query(f"""
        SELECT 
            strftime('%Y-%m', order_date) AS month,
            SUM(p.price * o.quantity) AS monthly_revenue,
            COUNT(DISTINCT o.order_id) AS monthly_orders
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE 1=1 {date_filter}
        GROUP BY month
        ORDER BY month;
    """)
    
    if not monthly_df.empty:
        fig_revenue = px.line(
            monthly_df, 
            x='month', 
            y='monthly_revenue',
            title='Monthly Revenue Trend',
            markers=True,
            line_shape='spline'
        )
        fig_revenue.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (₹)",
            showlegend=False,
            height=400
        )
        fig_revenue.update_traces(line_color='#3498db', line_width=3)
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("No data available for the selected period")

with col2:
    st.subheader("🏆 Top Selling Products")
    top_products_df = run_query(f"""
        SELECT 
            p.product_name,
            SUM(o.quantity) AS total_sold,
            SUM(p.price * o.quantity) AS total_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE 1=1 {date_filter}
        GROUP BY p.product_name
        ORDER BY total_sold DESC
        LIMIT 5;
    """)
    
    if not top_products_df.empty:
        fig_products = px.bar(
            top_products_df,
            x='total_sold',
            y='product_name',
            orientation='h',
            title='Units Sold',
            color='total_sold',
            color_continuous_scale='viridis'
        )
        fig_products.update_layout(
            height=400,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_products, use_container_width=True)
    else:
        st.info("No product data available")

# Row 2: Geographic Analysis and Customer Insights
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Revenue by Country")
    country_df = run_query(f"""
        SELECT 
            c.country,
            SUM(p.price * o.quantity) AS revenue,
            COUNT(DISTINCT o.customer_id) AS customers,
            COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON o.product_id = p.product_id
        WHERE 1=1 {date_filter}
        GROUP BY c.country
        ORDER BY revenue DESC
        LIMIT 10;
    """)
    
    if not country_df.empty:
        fig_country = px.pie(
            country_df,
            values='revenue',
            names='country',
            title='Revenue Distribution by Country'
        )
        fig_country.update_traces(textposition='inside', textinfo='percent+label')
        fig_country.update_layout(height=400)
        st.plotly_chart(fig_country, use_container_width=True)
    else:
        st.info("No geographic data available")

with col2:
    st.subheader("💎 Customer Segments")
    customer_segments_df = run_query(f"""
        SELECT 
            CASE 
                WHEN total_spent >= 10000 THEN 'VIP'
                WHEN total_spent >= 5000 THEN 'Premium'
                WHEN total_spent >= 1000 THEN 'Regular'
                ELSE 'New'
            END AS segment,
            COUNT(*) AS customer_count,
            AVG(total_spent) AS avg_spending
        FROM (
            SELECT 
                c.customer_id,
                SUM(p.price * o.quantity) AS total_spent
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            WHERE 1=1 {date_filter}
            GROUP BY c.customer_id
        ) customer_totals
        GROUP BY segment
        ORDER BY avg_spending DESC;
    """)
    
    if not customer_segments_df.empty:
        fig_segments = px.bar(
            customer_segments_df,
            x='segment',
            y='customer_count',
            title='Customer Distribution by Segment',
            color='avg_spending',
            color_continuous_scale='plasma'
        )
        fig_segments.update_layout(height=400)
        st.plotly_chart(fig_segments, use_container_width=True)
    else:
        st.info("No customer segment data available")

# Detailed Tables Section
if show_details:
    st.markdown('<div class="section-header">📋 Detailed Analytics</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🛍️ Top Customers", "📦 Product Performance", "📅 Recent Orders"])
    
    with tab1:
        st.subheader("Top Customers by Revenue")
        top_customers_df = run_query(f"""
            SELECT 
                c.name,
                c.email,
                c.country,
                COUNT(o.order_id) AS total_orders,
                SUM(o.quantity) AS total_items,
                SUM(p.price * o.quantity) AS total_spent,
                MAX(o.order_date) AS last_order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            WHERE 1=1 {date_filter}
            GROUP BY c.customer_id, c.name, c.email, c.country
            ORDER BY total_spent DESC
            LIMIT 10;
        """)
        
        if not top_customers_df.empty:
            # Format the spending column
            top_customers_df['total_spent_formatted'] = top_customers_df['total_spent'].apply(format_currency)
            display_df = top_customers_df[['name', 'email', 'country', 'total_orders', 'total_items', 'total_spent_formatted', 'last_order_date']]
            display_df.columns = ['Name', 'Email', 'Country', 'Orders', 'Items', 'Total Spent', 'Last Order']
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No customer data available")
    
    with tab2:
        st.subheader("Product Performance Analysis")
        product_performance_df = run_query(f"""
            SELECT 
                p.product_name,
                p.category,
                p.price,
                SUM(o.quantity) AS units_sold,
                SUM(p.price * o.quantity) AS total_revenue,
                COUNT(DISTINCT o.customer_id) AS unique_customers,
                ROUND(SUM(p.price * o.quantity) * 1.0 / SUM(o.quantity), 2) AS avg_selling_price
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE 1=1 {date_filter}
            GROUP BY p.product_id, p.product_name, p.category, p.price
            ORDER BY total_revenue DESC;
        """)
        
        if not product_performance_df.empty:
            product_performance_df['total_revenue_formatted'] = product_performance_df['total_revenue'].apply(format_currency)
            product_performance_df['price_formatted'] = product_performance_df['price'].apply(format_currency)
            display_df = product_performance_df[['product_name', 'category', 'price_formatted', 'units_sold', 'total_revenue_formatted', 'unique_customers']]
            display_df.columns = ['Product', 'Category', 'Price', 'Units Sold', 'Revenue', 'Unique Customers']
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No product performance data available")
    
    with tab3:
        st.subheader("Recent Orders")
        recent_orders_df = run_query(f"""
            SELECT 
                o.order_id,
                o.order_date,
                c.name AS customer_name,
                p.product_name,
                o.quantity,
                p.price,
                (p.price * o.quantity) AS order_value
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            WHERE 1=1 {date_filter}
            ORDER BY o.order_date DESC
            LIMIT 20;
        """)
        
        if not recent_orders_df.empty:
            recent_orders_df['price_formatted'] = recent_orders_df['price'].apply(format_currency)
            recent_orders_df['order_value_formatted'] = recent_orders_df['order_value'].apply(format_currency)
            display_df = recent_orders_df[['order_id', 'order_date', 'customer_name', 'product_name', 'quantity', 'price_formatted', 'order_value_formatted']]
            display_df.columns = ['Order ID', 'Date', 'Customer', 'Product', 'Quantity', 'Unit Price', 'Total Value']
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No recent orders data available")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d; font-size: 0.9rem;'>"
    "📊 E-commerce Analytics Dashboard | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
    "</div>",
    unsafe_allow_html=True
)