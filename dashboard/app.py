
import os
import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Retail Sales BI Dashboard",
    page_icon="📊",
    layout="wide"
)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("WAREHOUSE_DB", "retail_warehouse"),
    "user": os.getenv("DB_USER", "dwuser"),
    "password": os.getenv("DB_PASSWORD", ""),
}


@st.cache_data(ttl=60)
def load_sales_data():
    connection = psycopg2.connect(**DB_CONFIG)

    query = """
        SELECT
            f.order_id,
            d.full_date AS order_date,
            p.product_name,
            p.category,
            r.region_name,
            r.state_name,
            f.quantity,
            f.unit_price,
            f.sales_amount
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        JOIN dim_product p
            ON f.product_key = p.product_key
        JOIN dim_region r
            ON f.region_key = r.region_key
        ORDER BY d.full_date;
    """

    try:
        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


st.title("📊 Retail Sales Business Intelligence")
st.caption("Traditional Data Warehouse | PostgreSQL + Python + Streamlit")

try:
    df = load_sales_data()
except Exception as error:
    st.error("Unable to connect to the warehouse database.")
    st.code(str(error))
    st.info(
        "Check that Docker Desktop is running and "
        "the PostgreSQL container is started."
    )
    st.stop()

if df.empty:
    st.warning("No sales records found. Run the ETL pipeline first.")
    st.stop()

df["order_date"] = pd.to_datetime(df["order_date"])

st.sidebar.header("Dashboard Filters")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_categories = st.sidebar.multiselect(
    "Product categories",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)

selected_products = st.sidebar.multiselect(
    "Products",
    options=sorted(df["product_name"].unique()),
    default=sorted(df["product_name"].unique())
)

selected_regions = st.sidebar.multiselect(
    "Regions",
    options=sorted(df["region_name"].unique()),
    default=sorted(df["region_name"].unique())
)

filtered_df = df[
    df["category"].isin(selected_categories)
    & df["product_name"].isin(selected_products)
    & df["region_name"].isin(selected_regions)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        filtered_df["order_date"].dt.date.between(
            start_date, end_date
        )
    ]
else:
    filtered_df = filtered_df.iloc[0:0]

st.subheader("Sales Overview")

total_revenue = filtered_df["sales_amount"].sum()
total_orders = filtered_df["order_id"].nunique()
total_units = filtered_df["quantity"].sum()
average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{total_units:,}")
col4.metric("Average Order Value", f"₹{average_order_value:,.2f}")

if filtered_df.empty:
    st.warning("No sales records match the selected filters.")
    st.stop()

st.divider()
st.subheader("Sales Analysis")

monthly_df = (
    filtered_df.assign(
        month=filtered_df["order_date"].dt.to_period("M").astype(str)
    )
    .groupby("month", as_index=False)["sales_amount"]
    .sum()
)

product_df = (
    filtered_df.groupby("product_name", as_index=False)
    .agg(
        revenue=("sales_amount", "sum"),
        units_sold=("quantity", "sum")
    )
    .sort_values("revenue", ascending=False)
)

category_df = (
    filtered_df.groupby("category", as_index=False)["sales_amount"]
    .sum()
)

region_df = (
    filtered_df.groupby("region_name", as_index=False)["sales_amount"]
    .sum()
    .sort_values("sales_amount", ascending=False)
)

left, right = st.columns(2)

with left:
    st.markdown("#### Monthly Revenue Trend")
    fig = px.line(
        monthly_df,
        x="month",
        y="sales_amount",
        markers=True,
        labels={
            "month": "Month",
            "sales_amount": "Revenue (₹)"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("#### Revenue by Product")
    fig = px.bar(
        product_df,
        x="product_name",
        y="revenue",
        labels={
            "product_name": "Product",
            "revenue": "Revenue (₹)"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.markdown("#### Revenue by Category")
    fig = px.pie(
        category_df,
        names="category",
        values="sales_amount",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("#### Revenue by Region")
    fig = px.bar(
        region_df,
        x="region_name",
        y="sales_amount",
        labels={
            "region_name": "Region",
            "sales_amount": "Revenue (₹)"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Detailed Sales Records")

display_df = filtered_df.rename(
    columns={
        "order_id": "Order ID",
        "order_date": "Order Date",
        "product_name": "Product",
        "category": "Category",
        "region_name": "Region",
        "state_name": "State",
        "quantity": "Quantity",
        "unit_price": "Unit Price (₹)",
        "sales_amount": "Revenue (₹)"
    }
)

st.dataframe(display_df, use_container_width=True, hide_index=True)

csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered sales as CSV",
    data=csv_data,
    file_name="retail_sales_report.csv",
    mime="text/csv"
)

st.caption("Data source: PostgreSQL retail_warehouse | ETL-powered sales data")
