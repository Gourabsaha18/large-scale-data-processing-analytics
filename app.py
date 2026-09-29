# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #171a21;
    }

    section[data-testid="stSidebar"] h2 {
        font-size: 22px;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #9aa4b2;
        margin-bottom: 25px;
    }

    /* KPI cards */
    .kpi-card {
        background: #151922;
        border: 1px solid #2b303b;
        border-radius: 12px;
        padding: 20px;
        min-height: 120px;
    }

    .kpi-title {
        color: #b7beca;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 650;
        color: #f5f7fa;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .small-note {
        color: #8993a3;
        font-size: 13px;
    }

    /* Divider */
    hr {
        border-color: #2b303b;
    }

    /* Sidebar labels */
    label {
        font-weight: 500 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ANALYTICS_PATH = BASE_DIR / "data" / "processed" / "order_analytics"
ORDERS_PATH = BASE_DIR / "data" / "processed" / "orders_cleaned"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_analytics_data():

    df = pd.read_parquet(ANALYTICS_PATH)

    # Convert numeric columns
    numeric_columns = [
        "price",
        "freight_value",
        "delivery_days"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean text columns
    text_columns = [
        "customer_state",
        "product_category_name",
        "payment_type",
        "delivery_performance"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    return df


@st.cache_data
def load_order_dates():

    """
    Load purchase timestamps from orders_cleaned.

    order_analytics is item-level, while purchase timestamp is
    order-level. We therefore keep one timestamp per order.
    """

    try:

        orders = pd.read_parquet(ORDERS_PATH)

        required = [
            "order_id",
            "order_purchase_timestamp"
        ]

        available = [
            col for col in required
            if col in orders.columns
        ]

        if len(available) < 2:
            return None

        orders = orders[available].copy()

        orders["order_purchase_timestamp"] = pd.to_datetime(
            orders["order_purchase_timestamp"],
            errors="coerce"
        )

        orders = orders.drop_duplicates(
            subset=["order_id"]
        )

        return orders

    except Exception:
        return None


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_analytics_data()

except Exception as e:

    st.error(
        "Unable to load the analytics Parquet dataset."
    )

    st.code(str(e))

    st.info(
        "Make sure data/processed/order_analytics exists "
        "and PyArrow is installed."
    )

    st.stop()


# ============================================================
# PREPARE DATA
# ============================================================

orders_dates = load_order_dates()


if orders_dates is not None:

    df = df.merge(
        orders_dates,
        on="order_id",
        how="left"
    )


# Remove invalid revenue rows
df["price"] = df["price"].fillna(0)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Dashboard Filters")

st.sidebar.caption(
    "Use the filters below to explore the Olist dataset."
)


# Customer State
states = sorted(
    df["customer_state"]
    .dropna()
    .unique()
    .tolist()
)

selected_states = st.sidebar.multiselect(
    "Customer State",
    states,
    placeholder="Choose states"
)


# Product Category
categories = sorted(
    df["product_category_name"]
    .dropna()
    .unique()
    .tolist()
)

selected_categories = st.sidebar.multiselect(
    "Product Category",
    categories,
    placeholder="Choose categories"
)


# Payment Method
payment_methods = sorted(
    df["payment_type"]
    .dropna()
    .unique()
    .tolist()
)

selected_payments = st.sidebar.multiselect(
    "Payment Method",
    payment_methods,
    placeholder="Choose payment methods"
)


# Delivery Performance
delivery_types = sorted(
    df["delivery_performance"]
    .dropna()
    .unique()
    .tolist()
)

selected_delivery = st.sidebar.multiselect(
    "Delivery Performance",
    delivery_types,
    placeholder="Choose performance"
)


# Reset button
if st.sidebar.button(
    "Reset Filters",
    width="stretch"
):

    st.rerun()


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if selected_states:

    filtered_df = filtered_df[
        filtered_df["customer_state"].isin(
            selected_states
        )
    ]


if selected_categories:

    filtered_df = filtered_df[
        filtered_df["product_category_name"].isin(
            selected_categories
        )
    ]


if selected_payments:

    filtered_df = filtered_df[
        filtered_df["payment_type"].isin(
            selected_payments
        )
    ]


if selected_delivery:

    filtered_df = filtered_df[
        filtered_df["delivery_performance"].isin(
            selected_delivery
        )
    ]


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">Olist E-Commerce Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Large-Scale Data Processing & Analytics using
    PySpark, SQL, Parquet and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_revenue = filtered_df["price"].sum()

order_items = len(filtered_df)

unique_orders = filtered_df["order_id"].nunique()


if unique_orders > 0:
    average_order_value = total_revenue / unique_orders
else:
    average_order_value = 0


# Delivery rate
delivery_df = filtered_df[
    filtered_df["delivery_performance"].isin(
        ["On Time", "Late"]
    )
]

if len(delivery_df) > 0:

    late_count = (
        delivery_df["delivery_performance"]
        .eq("Late")
        .sum()
    )

    late_rate = (
        late_count / len(delivery_df)
    ) * 100

else:

    late_count = 0
    late_rate = 0


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value">
                ₹{total_revenue:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Order Items</div>
            <div class="kpi-value">
                {order_items:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Unique Orders</div>
            <div class="kpi-value">
                {unique_orders:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Order Value</div>
            <div class="kpi-value">
                ₹{average_order_value:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi5:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Late Delivery Rate</div>
            <div class="kpi-value">
                {late_rate:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)

st.divider()


# ============================================================
# 1. MONTHLY REVENUE TREND
# ============================================================

st.markdown(
    '<div class="section-title">Revenue Trend</div>',
    unsafe_allow_html=True
)

if (
    "order_purchase_timestamp" in filtered_df.columns
    and filtered_df["order_purchase_timestamp"].notna().any()
):

    trend_df = filtered_df.dropna(
        subset=["order_purchase_timestamp"]
    ).copy()

    trend_df["month"] = (
        trend_df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        trend_df
        .groupby("month", as_index=False)
        .agg(
            revenue=("price", "sum"),
            order_items=("order_id", "count")
        )
        .sort_values("month")
    )

    fig = px.line(
        monthly,
        x="month",
        y="revenue",
        markers=True,
        labels={
            "month": "Month",
            "revenue": "Revenue (₹)"
        }
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: ₹%{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        hovermode="x unified",
        xaxis=dict(
            type="category",
            tickangle=-45
        )
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

else:

    st.info(
        "Purchase timestamp is not available for the revenue trend."
    )


# ============================================================
# 2. TOP PRODUCT CATEGORIES
# ============================================================

st.markdown(
    '<div class="section-title">Top 10 Product Categories by Revenue</div>',
    unsafe_allow_html=True
)

category_df = (
    filtered_df
    .groupby("product_category_name", as_index=False)
    .agg(
        revenue=("price", "sum"),
        order_items=("order_id", "count")
    )
    .sort_values(
        "revenue",
        ascending=False
    )
    .head(10)
    .sort_values(
        "revenue",
        ascending=True
    )
)


fig_category = px.bar(
    category_df,
    x="revenue",
    y="product_category_name",
    orientation="h",
    text="revenue",
    labels={
        "revenue": "Revenue (₹)",
        "product_category_name": "Product Category"
    }
)


fig_category.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Revenue: ₹%{x:,.2f}<br>"
        "<extra></extra>"
    )
)


fig_category.update_layout(
    height=500,
    margin=dict(
        l=20,
        r=100,
        t=20,
        b=20
    ),
    yaxis=dict(
        automargin=True
    ),
    xaxis=dict(
        tickformat=","
    )
)


st.plotly_chart(
    fig_category,
    width="stretch"
)


# ============================================================
# 3. REVENUE BY CUSTOMER STATE
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">Revenue by Customer State</div>',
        unsafe_allow_html=True
    )

    state_df = (
        filtered_df
        .groupby("customer_state", as_index=False)
        .agg(
            revenue=("price", "sum"),
            order_items=("order_id", "count")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(10)
        .sort_values(
            "revenue",
            ascending=True
        )
    )

    fig_state = px.bar(
        state_df,
        x="revenue",
        y="customer_state",
        orientation="h",
        text="revenue",
        labels={
            "revenue": "Revenue (₹)",
            "customer_state": "State"
        }
    )

    fig_state.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Revenue: ₹%{x:,.2f}<br>"
            "<extra></extra>"
        )
    )

    fig_state.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=90,
            t=20,
            b=20
        ),
        yaxis=dict(
            automargin=True
        )
    )

    st.plotly_chart(
        fig_state,
        width="stretch"
    )


# ============================================================
# 4. PAYMENT METHOD
# ============================================================

with col2:

    st.markdown(
        '<div class="section-title">Payment Method Distribution</div>',
        unsafe_allow_html=True
    )

    payment_df = (
        filtered_df
        .groupby("payment_type", as_index=False)
        .agg(
            order_items=("order_id", "count")
        )
        .sort_values(
            "order_items",
            ascending=False
        )
    )

    fig_payment = px.pie(
        payment_df,
        names="payment_type",
        values="order_items",
        hole=0.55,
        labels={
            "payment_type": "Payment Method",
            "order_items": "Order Items"
        }
    )

    fig_payment.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Order Items: %{value:,}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    fig_payment.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        legend=dict(
            orientation="v"
        )
    )

    st.plotly_chart(
        fig_payment,
        width="stretch"
    )


# ============================================================
# 5. DELIVERY PERFORMANCE
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">Delivery Performance</div>',
    unsafe_allow_html=True
)


delivery_col1, delivery_col2 = st.columns(2)


# ------------------------------------------------------------
# DELIVERY COUNT
# ------------------------------------------------------------

with delivery_col1:

    delivery_count = (
        filtered_df
        .groupby(
            "delivery_performance",
            as_index=False
        )
        .agg(
            order_items=("order_id", "count")
        )
        .sort_values(
            "order_items",
            ascending=False
        )
    )

    fig_delivery_count = px.bar(
        delivery_count,
        x="delivery_performance",
        y="order_items",
        text="order_items",
        labels={
            "delivery_performance": "Delivery Performance",
            "order_items": "Order Items"
        }
    )

    fig_delivery_count.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Order Items: %{y:,}"
            "<extra></extra>"
        )
    )

    fig_delivery_count.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_delivery_count,
        width="stretch"
    )


# ------------------------------------------------------------
# AVERAGE DELIVERY DAYS
# ------------------------------------------------------------

with delivery_col2:

    avg_delivery = (
        filtered_df[
            filtered_df["delivery_performance"]
            .isin(["On Time", "Late"])
        ]
        .groupby(
            "delivery_performance",
            as_index=False
        )
        .agg(
            average_delivery_days=(
                "delivery_days",
                "mean"
            )
        )
    )

    fig_avg_delivery = px.bar(
        avg_delivery,
        x="delivery_performance",
        y="average_delivery_days",
        text="average_delivery_days",
        labels={
            "delivery_performance":
                "Delivery Performance",
            "average_delivery_days":
                "Average Delivery Days"
        }
    )

    fig_avg_delivery.update_traces(
        texttemplate="%{text:.1f} days",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Average: %{y:.2f} days"
            "<extra></extra>"
        )
    )

    fig_avg_delivery.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_avg_delivery,
        width="stretch"
    )


# ============================================================
# 6. REVENUE + ORDER ITEMS BY STATE TABLE
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">Customer State Summary</div>',
    unsafe_allow_html=True
)


state_summary = (
    filtered_df
    .groupby(
        "customer_state",
        as_index=False
    )
    .agg(
        revenue=("price", "sum"),
        order_items=("order_id", "count"),
        unique_orders=("order_id", "nunique")
    )
    .sort_values(
        "revenue",
        ascending=False
    )
)

state_summary["average_order_value"] = (
    state_summary["revenue"]
    / state_summary["unique_orders"]
)


state_summary = state_summary.rename(
    columns={
        "customer_state": "State",
        "revenue": "Revenue",
        "order_items": "Order Items",
        "unique_orders": "Unique Orders",
        "average_order_value": "Average Order Value"
    }
)


st.dataframe(
    state_summary.style.format(
        {
            "Revenue": "₹{:,.2f}",
            "Order Items": "{:,.0f}",
            "Unique Orders": "{:,.0f}",
            "Average Order Value": "₹{:,.2f}"
        }
    ),
    width="stretch",
    hide_index=True
)


# ============================================================
# FILTERED DATA SUMMARY
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">Filtered Dataset Summary</div>',
    unsafe_allow_html=True
)


summary_col1, summary_col2 = st.columns(2)


with summary_col1:

    st.metric(
        "Filtered Order Items",
        f"{len(filtered_df):,}"
    )


with summary_col2:

    st.metric(
        "Filtered Unique Orders",
        f"{filtered_df['order_id'].nunique():,}"
    )


# ============================================================
# DOWNLOAD BUTTON
# ============================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered Dataset",
    data=csv_data,
    file_name="olist_filtered_analytics.csv",
    mime="text/csv",
    width="stretch"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br>
    <div style="
        text-align:center;
        color:#737b89;
        font-size:13px;
        padding:20px;
    ">
        Built with PySpark • SQL • Parquet • Pandas • Plotly • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)