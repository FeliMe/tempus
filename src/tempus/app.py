"""Streamlit application for viewing time series data."""

import pandas as pd
import streamlit as st

from tempus.utils.data_loader import load_csv_data
from tempus.utils.plotter import LineDashStyle, create_time_series_chart

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

# --- Sidebar: Column Selection ---
st.sidebar.header("Column Selection")
selected_columns = st.sidebar.multiselect(
    "Select Columns",
    options=df.columns.tolist(),
    default=df.columns.tolist(),
)

# --- Sidebar: Time Series Controls ---
st.sidebar.header("Time Series Controls")
smoothing = st.sidebar.slider("Smoothing (Rolling Average)", min_value=1, max_value=50, value=1)

# Date range filtering (only if index is datetime)
if isinstance(df.index, pd.DatetimeIndex):
    min_date, max_date = df.index.min().date(), df.index.max().date()
    start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    df = df.loc[str(start_date):str(end_date)]

# --- Sidebar: Styling ---
st.sidebar.header("Styling")
line_styles: dict[str, LineDashStyle] = {
    "Solid": "solid",
    "Dash": "dash",
    "Dot": "dot",
    "Dash-Dot": "dashdot",
}
line_style = st.sidebar.selectbox("Line Style", options=list(line_styles.keys()), index=0)

use_custom_color = st.sidebar.checkbox("Use Custom Color", value=False)
custom_color = st.sidebar.color_picker("Line Color", value="#1f77b4") if use_custom_color else None

# --- Create and Display Chart ---
fig = create_time_series_chart(
    df=df,
    columns=selected_columns,
    smoothing_window=smoothing,
    line_dash=line_styles[line_style],
    line_color=custom_color,
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": True, "displayModeBar": True},
)
