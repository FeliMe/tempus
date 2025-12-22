"""Streamlit application for viewing time series data."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.title("Time Series Data Viewer")

# Move file uploader to sidebar for clean layout
st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Attempt to parse the first column as datetime and set as index
    first_col = df.columns[0]
    try:
        df[first_col] = pd.to_datetime(df[first_col])
        df = df.set_index(first_col)
    except (ValueError, TypeError):
        # Parsing failed, use default range index
        pass

    # Sidebar section for column selection
    st.sidebar.header("Column Selection")
    available_columns = df.columns.tolist()
    selected_columns = st.sidebar.multiselect(
        "Select Columns",
        options=available_columns,
        default=available_columns,
    )

    # Sidebar section for time series controls
    st.sidebar.header("Time Series Controls")

    # Smoothing control
    smoothing = st.sidebar.slider("Smoothing (Rolling Average)", min_value=1, max_value=50, value=1)

    # Date range filtering (only if index is datetime)
    if isinstance(df.index, pd.DatetimeIndex):
        min_date = df.index.min().date()
        max_date = df.index.max().date()
        start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
        # Filter dataframe by date range
        df = df.loc[str(start_date):str(end_date)]

    # Sidebar section for styling
    st.sidebar.header("Styling")

    # Line style selector
    line_styles = {"Solid": "solid", "Dash": "dash", "Dot": "dot", "Dash-Dot": "dashdot"}
    line_style = st.sidebar.selectbox("Line Style", options=list(line_styles.keys()), index=0)

    # Color picker for global line color (optional, leave blank for auto colors)
    use_custom_color = st.sidebar.checkbox("Use Custom Color", value=False)
    custom_color = None
    if use_custom_color:
        custom_color = st.sidebar.color_picker("Line Color", value="#1f77b4")

    # Apply smoothing if needed
    plot_df = df.copy()
    if smoothing > 1:
        plot_df = plot_df.rolling(window=smoothing, min_periods=1).mean()

    # Create and display the plot
    fig = go.Figure()
    for col in selected_columns:
        trace_kwargs = {
            "x": plot_df.index,
            "y": plot_df[col],
            "name": col,
            "line": {"dash": line_styles[line_style]},
        }
        if custom_color:
            trace_kwargs["line"]["color"] = custom_color
        fig.add_trace(go.Scatter(**trace_kwargs))

    # Update layout for better visual appeal
    fig.update_layout(
        title="Time Series Plot",
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode="x unified",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgray",
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    # Render plot with zoom/pan enabled (native Plotly config)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        },
    )
else:
    st.info("👈 Upload a CSV file from the sidebar to get started.")
