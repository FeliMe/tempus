"""Streamlit application for viewing time series data."""

import streamlit as st

from tempus.utils.data_loader import load_csv_data
from tempus.utils.plotter import create_time_series_chart

# Page config
st.title("Time Series Data Viewer")

# --- Sidebar: File Upload ---
st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("👈 Upload a CSV file from the sidebar to get started.")
    st.stop()

# --- Load Data ---
try:
    df = load_csv_data(uploaded_file)
except ValueError as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# Use all columns by default
selected_columns = df.columns.tolist()

# --- Create and Display Chart ---
fig = create_time_series_chart(
    df=df,
    columns=selected_columns,
)

st.plotly_chart(
    fig,
    width="stretch",
    config={"scrollZoom": True, "displayModeBar": True, "doubleClickDelay": 500},
)
