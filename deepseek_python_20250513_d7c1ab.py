import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Order Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data function with caching
@st.cache_data
def load_data(file_path):
    # Read CSV file
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # Clean and preprocess data
    # Convert date columns to datetime
    date_cols = ['Order Date', 'Detail Order Date', 'Start Date', 'End Date', 'Payment Status Date', 'Payment Received Date', 'Invoice Date']
    for col in date_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
            except:
                df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Clean numeric columns
    numeric_cols = ['Qty', 'Unit Qty', 'Unit Price', 'Sub Total', 'Total Payment', 
                    'Total transaction', 'Trx (after disc)', 'Discount', 'Balance']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
    
    # Extract month and year from order date
    if 'Order Date' in df.columns:
        df['Order Month'] = df['Order Date'].dt.to_period('M')
        df['Order Year'] = df['Order Date'].dt.year
    
    return df

# Main function
def main():
    # Load data
    df = load_data('Testdetailorders.csv')
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = df['Order Date'].min().date()
    max_date = df['Order Date'].max().date()
    date_range = st.sidebar.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Convert date_range to datetime
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    
    # Apply date filter
    filtered_df = df[(df['Order Date'] >= start_date) & (df['Order Date'] <= end_date)]
    
    # Order Status filter
    status_options = ['All'] + list(filtered_df['Order Status'].unique())
    selected_status = st.sidebar.selectbox("Order Status", status_options)
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Order Status'] == selected_status]
    
    # Payment Status filter
    payment_options = ['All'] + list(filtered_df['Payment Status'].unique())
    selected_payment = st.sidebar.selectbox("Payment Status", payment_options)
    if selected_payment != 'All':
        filtered_df = filtered_df[filtered_df['Payment Status'] == selected_payment]
    
    # Product Type filter
    product_options = ['All'] + list(filtered_df['Tipe Produk'].unique())
    selected_product = st.sidebar.selectbox("Product Type", product_options)
    if selected_product != 'All':
        filtered_df = filtered_df[filtered_df['Tipe Produk'] == selected_product]
    
    # Order Source filter
    source_options = ['All'] + list(filtered_df['Order Source'].unique())
    selected_source = st.sidebar.selectbox("Order Source", source_options)
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['Order Source'] == selected_source]
    
    # Main dashboard
    st.title("📊 Order Analytics Dashboard")
    
    # KPI cards
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = len(filtered_df)
        st.metric("Total Orders", value=f"{total_orders:,}")
    
    with col2:
        total_revenue = filtered_df['Sub Total'].sum()
        st.metric("Total Revenue", value=f"${total_revenue:,.2f}")
    
    with col3:
        avg_order_value = filtered_df['Sub Total'].mean()
        st.metric("Avg Order Value", value=f"${avg_order_value:,.2f}")
    
    with col4:
        unique_customers = filtered_df['Create by'].nunique()
        st.metric("Unique Customers", value=f"{unique_customers:,}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Revenue Analysis", "Product Performance", "Raw Data"])
    
    with tab1:
        st.subheader("Order Overview")
        
        # Time series chart
        col1, col2 = st.columns([3, 1])
        
        with col1:
            time_series_df = filtered_df.groupby('Order Date').agg(
                Orders=('Order ID', 'count'),
                Revenue=('Sub Total', 'sum')
            ).reset_index()
            
            fig = px.line(
                time_series_df,
                x='Order Date',
                y='Orders',
                title='Daily Order Trend',
                labels={'Order Date': 'Date', 'Orders': 'Number of Orders'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("Top Order Statuses")
            status_counts = filtered_df['Order Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            st.dataframe(status_counts, hide_index=True)
    
    with tab2:
        st.subheader("Revenue Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by product type
            revenue_by_product = filtered_df.groupby('Tipe Produk')['Sub Total'].sum().reset_index()
            revenue_by_product = revenue_by_product.sort_values('Sub Total', ascending=False)
            
            fig = px.bar(
                revenue_by_product,
                x='Tipe Produk',
                y='Sub Total',
                title='Revenue by Product Type',
                labels={'Tipe Produk': 'Product Type', 'Sub Total': 'Revenue'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue by order source
            revenue_by_source = filtered_df.groupby('Order Source')['Sub Total'].sum().reset_index()
            revenue_by_source = revenue_by_source.sort_values('Sub Total', ascending=False)
            
            fig = px.pie(
                revenue_by_source,
                names='Order Source',
                values='Sub Total',
                title='Revenue by Order Source'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Product Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top products by revenue
            top_products = filtered_df.groupby('Product Name')['Sub Total'].sum().reset_index()
            top_products = top_products.sort_values('Sub Total', ascending=False).head(10)
            
            fig = px.bar(
                top_products,
                x='Product Name',
                y='Sub Total',
                title='Top 10 Products by Revenue',
                labels={'Product Name': 'Product', 'Sub Total': 'Revenue'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top products by quantity
            top_qty = filtered_df.groupby('Product Name')['Qty'].sum().reset_index()
            top_qty = top_qty.sort_values('Qty', ascending=False).head(10)
            
            fig = px.bar(
                top_qty,
                x='Product Name',
                y='Qty',
                title='Top 10 Products by Quantity Sold',
                labels={'Product Name': 'Product', 'Qty': 'Quantity'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Raw Data")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_orders.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()