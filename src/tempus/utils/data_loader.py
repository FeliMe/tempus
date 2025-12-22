"""Utility functions for loading and processing CSV data."""

from typing import BinaryIO

import pandas as pd
import streamlit as st


@st.cache_data
def load_csv_data(file: BinaryIO) -> pd.DataFrame:
    """Load CSV data from an uploaded file and process it into a DataFrame.

    Args:
        file: A file-like object containing CSV data.

    Returns:
        A pandas DataFrame with the CSV data. If the first column can be
        parsed as datetime, it will be set as the index.

    Raises:
        ValueError: If the file is empty or has invalid CSV format.
    """
    try:
        df = pd.read_csv(file)
    except pd.errors.EmptyDataError as e:
        raise ValueError("The uploaded file is empty.") from e
    except pd.errors.ParserError as e:
        raise ValueError(f"Invalid CSV format: {e}") from e

    if df.empty:
        raise ValueError("The CSV file contains no data.")

    # Check if index is already a DatetimeIndex
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    # Attempt to parse the first column as datetime and set as index
    first_col = df.columns[0]
    try:
        df[first_col] = pd.to_datetime(df[first_col])
        df = df.set_index(first_col)
    except (ValueError, TypeError):
        # Parsing failed, keep default range index
        pass

    return df
