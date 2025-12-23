"""Utility functions for loading and processing CSV data."""

from typing import BinaryIO

import pandas as pd
import streamlit as st


@st.cache_data
def load_csv_data(file: BinaryIO) -> pd.DataFrame:
    """Load CSV data from an uploaded file and process it into a DataFrame.

    Supports both standard CSV format and German format (semicolon separator,
    comma decimal). Uses PyArrow for faster parsing of large files.

    Args:
        file: A file-like object containing CSV data.

    Returns:
        A pandas DataFrame with the CSV data. If datetime columns are found,
        they will be combined and set as the index.

    Raises:
        ValueError: If the file is empty or has invalid CSV format.
    """
    try:
        # First, try German format (semicolon separator, comma decimal)
        # Note: PyArrow engine doesn't support decimal parameter, so we use default engine for German format
        df = pd.read_csv(file, sep=";", decimal=",")

        # If only one column, it wasn't semicolon-separated, try comma with PyArrow
        if len(df.columns) == 1:
            file.seek(0)
            df = pd.read_csv(file, engine="pyarrow", dtype_backend="pyarrow")
    except pd.errors.EmptyDataError as e:
        raise ValueError("The uploaded file is empty.") from e
    except pd.errors.ParserError as e:
        raise ValueError(f"Invalid CSV format: {e}") from e

    if df.empty:
        raise ValueError("The CSV file contains no data.")

    # Check if index is already a DatetimeIndex
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    # Handle German temperature data format with separate Datum and Uhrzeit columns
    if "Datum" in df.columns and "Uhrzeit" in df.columns:
        # Combine Datum and Uhrzeit into a single datetime index
        df["Datetime"] = pd.to_datetime(df["Datum"])
        df = df.drop(columns=["Datum", "Uhrzeit"])
        df = df.set_index("Datetime")
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
