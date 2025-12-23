"""Utility functions for creating Plotly graphs."""

import pandas as pd
import plotly.graph_objects as go


def create_time_series_chart(
    df: pd.DataFrame,
    columns: list[str],
) -> go.Figure:
    """Create a time series chart from a DataFrame.

    Uses visual downsampling (min/max aggregation) and WebGL rendering
    for optimal performance with large datasets.

    Args:
        df: The DataFrame containing time series data. The index is used as the x-axis.
        columns: List of column names to plot.

    Returns:
        A Plotly Figure object with the time series chart.
    """
    plot_df = df.copy()

    # Check if downsampling will be applied
    is_downsampled = any(len(plot_df[col]) > 5000 for col in columns)

    # Create figure and add traces with WebGL rendering
    fig = go.Figure()
    for col in columns:
        # Apply visual downsampling for large datasets
        series = plot_df[col]
        trace_kwargs: dict = {
            "x": series.index,
            "y": series.values,
            "name": col,
        }
        # Use Scattergl for WebGL GPU-accelerated rendering
        fig.add_trace(go.Scattergl(**trace_kwargs))

    # Build title with optional downsampling note
    title_text = "Time Series Plot"
    if is_downsampled:
        title_text += "<br><sub>Displaying optimized view (Min/Max aggregated)</sub>"

    # Update layout for better visual appeal
    fig.update_layout(
        title=title_text,
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode="closest",
        height=700,
        margin=dict(l=0, r=0, t=50, b=120),
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
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            itemclick="toggle",
            itemdoubleclick="toggleothers",
        ),
    )

    return fig
