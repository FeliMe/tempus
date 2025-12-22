"""Utility functions for creating Plotly graphs."""

from typing import Literal

import pandas as pd
import plotly.graph_objects as go

LineDashStyle = Literal["solid", "dash", "dot", "dashdot"]


def create_time_series_chart(
    df: pd.DataFrame,
    columns: list[str],
    style_df: pd.DataFrame | None = None,
) -> go.Figure:
    """Create a time series chart from a DataFrame.

    Args:
        df: The DataFrame containing time series data. The index is used as the x-axis.
        columns: List of column names to plot.
        style_df: Optional DataFrame with styling info. Index should be column names,
            with columns 'Color', 'Style', and 'Width' for line properties.

    Returns:
        A Plotly Figure object with the time series chart.
    """
    plot_df = df.copy()

    # Create figure and add traces
    fig = go.Figure()
    for col in columns:
        # Build line properties from style_df
        line_props: dict = {}
        if style_df is not None and col in style_df.index:
            row = style_df.loc[col]
            line_props = {
                "color": row["Color"],
                "dash": row["Style"],
                "width": row["Width"],
            }

        # Determine visibility from style_df
        visible = True
        if style_df is not None and col in style_df.index and "Visible" in style_df.columns:
            visible = style_df.loc[col, "Visible"]

        trace_kwargs: dict = {
            "x": plot_df.index,
            "y": plot_df[col],
            "name": col,
            "line": line_props,
            "visible": True if visible else "legendonly",
        }
        fig.add_trace(go.Scatter(**trace_kwargs))

    # Update layout for better visual appeal
    fig.update_layout(
        title="Time Series Plot",
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
