"""Data model for handling large CSV time-series data."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal


class DataModel(QObject):
    """Model for loading and managing time-series data from CSV files.

    Handles European-format CSVs (semicolon separator, comma decimal) as well as
    standard formats. Optimized for large datasets with millions of rows.
    """

    # Signals
    data_loaded = pyqtSignal(str)  # Emitted when data is loaded, with filename
    data_cleared = pyqtSignal()
    error_occurred = pyqtSignal(str)  # Emitted on errors, with error message

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._dataframe: pd.DataFrame | None = None
        self._filename: str = ""
        self._numeric_columns: list[str] = []
        self._time_column: str | None = None
        self._time_values: np.ndarray | None = None
        self._datetime_values: pd.DatetimeIndex | None = None

    @property
    def dataframe(self) -> pd.DataFrame | None:
        """Get the loaded DataFrame."""
        return self._dataframe

    @property
    def filename(self) -> str:
        """Get the loaded filename."""
        return self._filename

    @property
    def numeric_columns(self) -> list[str]:
        """Get list of numeric column names available for plotting."""
        return self._numeric_columns

    @property
    def time_values(self) -> np.ndarray | None:
        """Get the time/index values as numpy array for plotting."""
        return self._time_values

    @property
    def datetime_values(self) -> pd.DatetimeIndex | None:
        """Get the datetime values as DatetimeIndex for axis formatting."""
        return self._datetime_values

    @property
    def row_count(self) -> int:
        """Get the number of rows in the dataset."""
        return len(self._dataframe) if self._dataframe is not None else 0

    def load_csv(self, filepath: str | Path) -> bool:
        """Load a CSV file, auto-detecting format.

        Supports:
        - European format: semicolon separator, comma decimal (e.g., "1,5" = 1.5)
        - Standard format: comma separator, period decimal

        Args:
            filepath: Path to the CSV file

        Returns:
            True if loading succeeded, False otherwise
        """
        filepath = Path(filepath)
        if not filepath.exists():
            self.error_occurred.emit(f"File not found: {filepath}")
            return False

        try:
            # First, detect the format by reading a sample
            with open(filepath, encoding="utf-8") as f:
                sample = f.read(4096)

            # Detect separator
            semicolon_count = sample.count(";")
            comma_count = sample.count(",")

            if semicolon_count > comma_count:
                # European format
                separator = ";"
                decimal = ","
            else:
                # Standard format
                separator = ","
                decimal = "."

            # Load the data with detected format
            # Use pyarrow backend for better performance on large files
            df = pd.read_csv(
                filepath,
                sep=separator,
                decimal=decimal,
                engine="pyarrow",
                dtype_backend="pyarrow",
            )

            # Process the dataframe
            self._process_dataframe(df, filepath.name)
            return True

        except Exception as e:
            self.error_occurred.emit(f"Error loading CSV: {e}")
            return False

    def _process_dataframe(self, df: pd.DataFrame, filename: str) -> None:
        """Process the loaded dataframe, identifying columns and preparing data."""
        self._dataframe = df
        self._filename = filename

        # Identify numeric columns (exclude time/date columns)
        self._numeric_columns = []
        self._time_column = None

        # Look for time/date columns
        for col in df.columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ["datum", "date", "time", "timestamp", "uhrzeit"]):
                if self._time_column is None:
                    self._time_column = col
                continue

            # Check if column is numeric
            try:
                # Convert to numeric if not already
                if df[col].dtype in [np.float64, np.int64, "float64[pyarrow]", "int64[pyarrow]", "double[pyarrow]"]:
                    self._numeric_columns.append(col)
                elif pd.api.types.is_numeric_dtype(df[col]):
                    self._numeric_columns.append(col)
            except (ValueError, TypeError):
                pass

        # Create time values array (use index if no time column found)
        if self._time_column is not None:
            try:
                # Try to parse as datetime
                time_series = pd.to_datetime(df[self._time_column], errors="coerce")
                if time_series.notna().any():
                    # Store datetime values for axis formatting
                    self._datetime_values = pd.DatetimeIndex(time_series)
                    # Convert to numeric (timestamp in seconds for plotting)
                    self._time_values = time_series.astype(np.int64).to_numpy() / 1e9  # Convert to Unix timestamp
                else:
                    self._datetime_values = None
                    self._time_values = np.arange(len(df))
            except Exception:
                self._datetime_values = None
                self._time_values = np.arange(len(df))
        else:
            self._datetime_values = None
            self._time_values = np.arange(len(df))

        self.data_loaded.emit(filename)

    def get_column_data(self, column: str) -> np.ndarray | None:
        """Get the data for a specific column as a numpy array.

        Args:
            column: Column name

        Returns:
            Numpy array of values, or None if column doesn't exist
        """
        if self._dataframe is None or column not in self._dataframe.columns:
            return None

        return self._dataframe[column].to_numpy(dtype=np.float64, na_value=np.nan)

    def get_smoothed_data(self, column: str, window: int) -> np.ndarray | None:
        """Get smoothed data using rolling average with caching.

        Args:
            column: Column name
            window: Rolling window size (1 = no smoothing)

        Returns:
            Numpy array of smoothed values, or None if column doesn't exist
        """
        if self._dataframe is None or column not in self._dataframe.columns:
            return None

        if window <= 1:
            return self.get_column_data(column)

        # Use cached computation for better performance
        return self._compute_smoothed_data(column, window)

    @lru_cache(maxsize=128)
    def _compute_smoothed_data(self, column: str, window: int) -> np.ndarray:
        """Cached computation of smoothed data.

        Args:
            column: Column name
            window: Rolling window size

        Returns:
            Numpy array of smoothed values
        """
        assert self._dataframe is not None
        series = self._dataframe[column]
        smoothed = series.rolling(window=window, center=True, min_periods=1).mean()
        return smoothed.to_numpy(dtype=np.float64)

    def clear(self) -> None:
        """Clear all loaded data."""
        self._dataframe = None
        self._filename = ""
        self._numeric_columns = []
        self._time_column = None
        self._time_values = None
        self._datetime_values = None
        # Clear the smoothing cache
        self._compute_smoothed_data.cache_clear()
        self.data_cleared.emit()

    def get_statistics(self, column: str) -> dict[str, Any]:
        """Get basic statistics for a column.

        Args:
            column: Column name

        Returns:
            Dictionary with min, max, mean, std statistics
        """
        if self._dataframe is None or column not in self._dataframe.columns:
            return {}

        series = self._dataframe[column]
        return {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "std": float(series.std()),
        }
