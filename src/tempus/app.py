"""Streamlit application for viewing time series data."""

import pandas as pd
import streamlit as st

from tempus.utils.data_loader import load_csv_data
from tempus.utils.plotter import create_time_series_chart

# Default colors (Plotly default color cycle)
DEFAULT_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]
LINE_STYLE_OPTIONS = ["solid", "dash", "dot", "dashdot"]

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

# --- Build Style DataFrame for Interactive Legend ---
# Initialize style_df in session state if not present or if columns changed
if "style_df" not in st.session_state or set(st.session_state.style_df.index) != set(selected_columns):
    style_data = {
        "Color": [DEFAULT_COLORS[i % len(DEFAULT_COLORS)] for i in range(len(selected_columns))],
        "Style": ["solid"] * len(selected_columns),
        "Width": [2] * len(selected_columns),
        "Visible": [True] * len(selected_columns),
    }
    st.session_state.style_df = pd.DataFrame(style_data, index=selected_columns)
# Ensure Visible column exists for existing style_df
elif "Visible" not in st.session_state.style_df.columns:
    st.session_state.style_df["Visible"] = True

# --- Create and Display Chart ---
fig = create_time_series_chart(
    df=df,
    columns=selected_columns,
    style_df=st.session_state.style_df,
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": True, "displayModeBar": True, "doubleClickDelay": 500},
)

# --- Series Configuration (Interactive Legend) ---
with st.expander("Series Configuration", expanded=False):
    if selected_columns:
        edited_style_df = st.data_editor(
            st.session_state.style_df,
            column_config={
                "Color": st.column_config.TextColumn(
                    "Color",
                    help="Enter a hex color (e.g., #FF5733)",
                ),
                "Style": st.column_config.SelectboxColumn(
                    "Style",
                    help="Line dash style",
                    options=LINE_STYLE_OPTIONS,
                ),
                "Width": st.column_config.NumberColumn(
                    "Width",
                    help="Line width (1-5)",
                    min_value=1,
                    max_value=5,
                    step=1,
                ),
                "Visible": st.column_config.CheckboxColumn(
                    "Visible",
                    help="Toggle series visibility",
                    default=True,
                ),
            },
            use_container_width=True,
            hide_index=False,
            key="style_editor",
        )
        # Update session state with edited values
        st.session_state.style_df = edited_style_df
    else:
        st.info("Select columns to configure styles.")
