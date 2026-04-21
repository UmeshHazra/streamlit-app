import streamlit as st
import pandas as pd
import plotly.express as px

px.defaults.template = "plotly_dark"

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Ola Dashboard", layout="wide")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Cleaned_OLA_DataSet.csv", encoding='latin1')
    return df.sample(5000)  # 🔥 LIMIT DATA FOR SPEED

with st.spinner("Loading Dashboard..."):
    df = load_data()

# ------------------ SIDEBAR ------------------
st.sidebar.title("🔍 Filters")

vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    df["Vehicle_Type"].dropna().unique(),
    default=df["Vehicle_Type"].dropna().unique()
)

status = st.sidebar.multiselect(
    "Booking Status",
    df["Booking_Status"].dropna().unique(),
    default=df["Booking_Status"].dropna().unique()
)

payment = st.sidebar.multiselect(
    "Payment Method",
    df["Payment_Method"].dropna().unique(),
    default=df["Payment_Method"].dropna().unique()
)

# ------------------ FILTER ------------------
filtered_df = df[
    (df["Vehicle_Type"].isin(vehicle)) &
    (df["Booking_Status"].isin(status)) &
    (df["Payment_Method"].isin(payment))
]

# ------------------ TITLE ------------------
st.title("🚗 Ola Ride Advanced Dashboard")

# ------------------ KPI ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rides", len(filtered_df))
col2.metric("Revenue", f"₹ {filtered_df['Booking_Value'].sum():,.0f}")
col3.metric("Avg Rating", f"{filtered_df['Customer_Rating'].mean():.2f}")
col4.metric("Avg Distance", f"{filtered_df['Ride_Distance'].mean():.2f} km")

# ------------------ CHART SELECTOR ------------------
chart_option = st.selectbox(
    "📊 Select Analysis",
    ["Overview", "Time Analysis", "Customer Analysis"]
)

# ================== OVERVIEW ==================
if chart_option == "Overview":

    col1, col2 = st.columns(2)

    # Vehicle Count
    with col1:
        vehicle_data = filtered_df["Vehicle_Type"].value_counts().reset_index()
        fig = px.bar(
            vehicle_data,
            x="Vehicle_Type",
            y="count",
            color="Vehicle_Type",
            title="🚗 Rides by Vehicle Type"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Booking Status
    with col2:
        status_data = filtered_df["Booking_Status"].value_counts().reset_index()
        fig = px.pie(
            status_data,
            names="Booking_Status",
            values="count",
            title="📌 Booking Status"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Treemap (Optimized)
    st.subheader("🌳 Revenue Treemap")

    tree_data = filtered_df.groupby(
        ["Vehicle_Type", "Payment_Method"]
    )["Booking_Value"].sum().reset_index()

    fig = px.treemap(
        tree_data,
        path=["Vehicle_Type", "Payment_Method"],
        values="Booking_Value",
        color="Booking_Value",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================== TIME ANALYSIS ==================
elif chart_option == "Time Analysis":

    st.subheader("📈 Revenue by Hour")

    time_data = filtered_df.groupby("Ride_Hour")["Booking_Value"].sum().reset_index()

    fig = px.line(
        time_data,
        x="Ride_Hour",
        y="Booking_Value",
        markers=True,
        color_discrete_sequence=["cyan"]
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📍 Ride Distance Distribution")

    fig = px.histogram(
        filtered_df,
        x="Ride_Distance",
        nbins=30,
        color="Vehicle_Type",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    st.plotly_chart(fig, use_container_width=True)

# ================== CUSTOMER ANALYSIS ==================
elif chart_option == "Customer Analysis":

    st.subheader("🏆 Top Customers")

    top_customers = filtered_df["Customer_ID"].value_counts().head(10).reset_index()

    fig = px.bar(
        top_customers,
        x="Customer_ID",
        y="count",
        color="count",
        color_continuous_scale="rainbow"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⭐ Rating Distribution")

    rating_data = filtered_df.groupby("Vehicle_Type")["Customer_Rating"].mean().reset_index()

    fig = px.bar(
        rating_data,
        x="Vehicle_Type",
        y="Customer_Rating",
        color="Vehicle_Type",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------ DATA TABLE ------------------
if st.checkbox("Show Data"):
    st.dataframe(filtered_df)
    
