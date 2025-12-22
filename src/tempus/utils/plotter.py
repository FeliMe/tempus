"""Utility functions for creating Plotly graphs."""

from typing import Literal

import pandas as pd
import plotly.graph_objects as go

LineDashStyle = Literal["solid", "dash", "dot", "dashdot"]


def create_time_series_chart(
    df: pd.DataFrame,
    columns: list[str],
    smoothing_window: int = 1,
    line_dash: LineDashStyle = "solid",
    line_color: str | None = None,
) -> go.Figure:
    """Create a time series chart from a DataFrame.

    Args:
        df: The DataFrame containing time series data. The index is used as the x-axis.
        columns: List of column names to plot.
        smoothing_window: Rolling average window size. Values > 1 apply smoothing.
        line_dash: Line style for all traces ("solid", "dash", "dot", or "dashdot").
        line_color: Optional custom color for all lines. If None, uses Plotly defaults.

    Returns:
        A Plotly Figure object with the time series chart.
    """
    # Apply smoothing if needed
    plot_df = df.copy()
    if smoothing_window > 1:
        plot_df = plot_df.rolling(window=smoothing_window, min_periods=1).mean()

    # Create figure and add traces
    fig = go.Figure()
    for col in columns:
        trace_kwargs: dict = {
            "x": plot_df.index,
            "y": plot_df[col],
            "name": col,
            "line": {"dash": line_dash},
        }
        if line_color:
            trace_kwargs["line"]["color"] = line_color
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

    return fig
