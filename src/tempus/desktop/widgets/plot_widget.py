"""High-performance plot widget using pyqtgraph."""

from datetime import datetime, timedelta

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from tempus.desktop.theme import ThemeManager


class DateTimeAxis(pg.AxisItem):
    """Custom axis that displays Unix timestamps as formatted datetime strings."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._datetime_format = "%Y-%m-%d %H:%M:%S"

    def tickStrings(self, values, scale, spacing):
        """Convert timestamp values to formatted datetime strings."""
        strings = []
        for value in values:
            try:
                dt = datetime.fromtimestamp(value)
                # Adapt format based on spacing (zoom level)
                if spacing > 86400:  # More than a day
                    fmt = "%Y-%m-%d"
                elif spacing > 3600:  # More than an hour
                    fmt = "%m-%d %H:%M"
                elif spacing > 60:  # More than a minute
                    fmt = "%H:%M:%S"
                else:
                    fmt = "%H:%M:%S"
                strings.append(dt.strftime(fmt))
            except (ValueError, OSError, OverflowError):
                strings.append(str(value))
        return strings


class CrosshairManager:
    """Manages crosshair overlay on the plot."""

    def __init__(self, plot_widget: pg.PlotWidget, datetime_axis: DateTimeAxis | None = None) -> None:
        self.plot_widget = plot_widget
        self.plot_item = plot_widget.getPlotItem()
        self._datetime_axis = datetime_axis
        self._parent_widget: TimeSeriesPlotWidget | None = None

        # Get theme colors
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()

        # Create crosshair lines
        pen = pg.mkPen(color=colors["crosshair_pen"], width=1, style=Qt.PenStyle.DashLine)
        self.v_line = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.h_line = pg.InfiniteLine(angle=0, movable=False, pen=pen)

        self.plot_item.addItem(self.v_line, ignoreBounds=True)
        self.plot_item.addItem(self.h_line, ignoreBounds=True)

        # Create label for coordinates (anchor top-right to avoid legend)
        self.label = pg.TextItem(anchor=(1, 0), color=colors["crosshair_label"])
        self.label.setFont(QFont("Monospace", 9))
        self.plot_item.addItem(self.label, ignoreBounds=True)

        # Connect mouse move
        scene = plot_widget.scene()
        assert scene is not None
        self.proxy = pg.SignalProxy(scene.sigMouseMoved, rateLimit=60, slot=self._on_mouse_moved)  # type: ignore[attr-defined]

        self._visible = True

    def set_parent_widget(self, parent: "TimeSeriesPlotWidget") -> None:
        """Set reference to parent widget for accessing series data."""
        self._parent_widget = parent

    def update_theme(self) -> None:
        """Update crosshair colors for current theme."""
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()

        pen = pg.mkPen(color=colors["crosshair_pen"], width=1, style=Qt.PenStyle.DashLine)
        self.v_line.setPen(pen)
        self.h_line.setPen(pen)
        self.label.setColor(colors["crosshair_label"])

    def _on_mouse_moved(self, evt) -> None:
        """Update crosshair position on mouse move."""
        pos = evt[0]
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_item.vb.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()

            self.v_line.setPos(x)
            self.h_line.setPos(y)

            # Update label - show datetime if available
            if self._datetime_axis is not None:
                try:
                    dt = datetime.fromtimestamp(x)
                    x_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, OSError, OverflowError):
                    x_str = f"{x:.2f}"
            else:
                x_str = f"{x:.2f}"

            # Find closest series
            series_name = self._find_closest_series(x, y)

            label_text = f"x={x_str}, y={y:.2f}"
            if series_name:
                label_text += f" [{series_name}]"
            self.label.setText(label_text)

            # Position label in top-right of view (to avoid legend)
            view_range = self.plot_item.viewRange()
            self.label.setPos(view_range[0][1], view_range[1][1])

    def set_visible(self, visible: bool) -> None:
        """Show or hide the crosshair."""
        self._visible = visible
        self.v_line.setVisible(visible)
        self.h_line.setVisible(visible)
        self.label.setVisible(visible)

    def _find_closest_series(self, x: float, y: float) -> str | None:
        """Find the series name closest to the given coordinates."""
        if self._parent_widget is None:
            return None

        series_data = self._parent_widget._series_data
        curves = self._parent_widget._curves

        if not series_data:
            return None

        closest_name = None
        min_dist = float("inf")

        y_range = self.plot_item.viewRange()[1]
        y_scale = y_range[1] - y_range[0] if y_range[1] != y_range[0] else 1

        for name, (x_data, y_data) in series_data.items():
            if name not in curves:
                continue
            if not curves[name].isVisible():
                continue
            if len(x_data) == 0:
                continue

            idx = np.searchsorted(x_data, x)
            idx = max(0, min(idx, len(y_data) - 1))

            dist = abs(y_data[idx] - y) / y_scale
            if dist < min_dist:
                min_dist = dist
                closest_name = name

        # Only return if within 15% of the y-range
        if min_dist < 0.15:
            return closest_name
        return None


class TimeSeriesPlotWidget(QWidget):
    """High-performance time-series plot widget with auto-downsampling.

    Features:
    - Auto-downsampling for smooth performance with millions of points
    - Dark theme with contrasting grid
    - Crosshair with coordinate display
    - Multiple series support
    """

    # Signals
    range_changed = pyqtSignal(float, float)  # x_min, x_max when view changes

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._series_data: dict[str, tuple[np.ndarray, np.ndarray]] = {}  # Store x,y data for range calc
        self._day_lines: list[pg.InfiniteLine] = []  # Day boundary lines
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the plot widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Get theme colors
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()

        # Configure pyqtgraph for current theme
        # Note: antialias=False is critical for performance with large datasets
        # and thick lines. Antialiasing thick lines is extremely expensive.
        pg.setConfigOptions(
            antialias=False,
            background=colors["background"],
            foreground=colors["foreground"],
        )

        # Create custom datetime axis for x-axis
        self._datetime_axis = DateTimeAxis(orientation="bottom")

        # Create plot widget with custom axis
        self._plot_widget = pg.PlotWidget(axisItems={"bottom": self._datetime_axis})
        layout.addWidget(self._plot_widget)

        # Get plot item for configuration
        self._plot_item = self._plot_widget.getPlotItem()

        # Configure axes
        self._plot_item.setLabel("bottom", "Time")
        self._plot_item.setLabel("left", "Value")

        # Enable grid with theme styling
        self._plot_item.showGrid(x=True, y=True, alpha=colors["grid_alpha"])

        # Configure axis appearance for current theme
        self._apply_axis_theme(colors)

        # Enable mouse interaction (X-axis only for time-series zoom)
        self._plot_item.setMouseEnabled(x=True, y=False)
        # Disable Y auto-range - we'll manage it manually to include hidden series
        self._plot_item.disableAutoRange(axis="y")

        # Add crosshair with datetime awareness
        self._crosshair = CrosshairManager(self._plot_widget, self._datetime_axis)
        self._crosshair.set_parent_widget(self)

        # Connect range change signal
        self._plot_item.sigRangeChanged.connect(self._on_range_changed)

        # Store current title for theme updates
        self._current_title: str | None = None

        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_axis_theme(self, colors: dict) -> None:
        """Apply theme colors to axes."""
        axis_pen = pg.mkPen(color=colors["axis_pen"], width=1)
        for axis_name in ["bottom", "left", "top", "right"]:
            axis = self._plot_item.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(pg.mkPen(color=colors["axis_text"]))

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change."""
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()

        # Update plot background
        self._plot_widget.setBackground(colors["background"])

        # Update axes
        self._apply_axis_theme(colors)

        # Update grid
        self._plot_item.showGrid(x=True, y=True, alpha=colors["grid_alpha"])

        # Update crosshair
        self._crosshair.update_theme()

        # Update day boundary lines
        self.update_day_boundary_theme()

        # Update title if set
        if self._current_title:
            self._plot_item.setTitle(self._current_title, color=colors["title_color"], size="12pt")

    def add_series(
        self,
        name: str,
        x_data: np.ndarray,
        y_data: np.ndarray,
        color: QColor | str = "#1f77b4",
        width: int = 1,
    ) -> None:
        """Add or update a data series.

        Args:
            name: Series identifier
            x_data: X values (time indices)
            y_data: Y values
            color: Line color (QColor or hex string)
            width: Line width in pixels
        """
        if isinstance(color, QColor):
            color = color.name()

        pen = pg.mkPen(color=color, width=width)

        # Store data for range calculations (includes hidden series)
        self._series_data[name] = (x_data, y_data)

        if name in self._curves:
            # Update existing curve
            curve = self._curves[name]
            curve.setData(x_data, y_data)
            curve.setPen(pen)
        else:
            # Create new curve with auto-downsampling for performance
            curve = self._plot_item.plot(
                x_data,
                y_data,
                pen=pen,
                name=name,
                # Enable downsampling for large datasets
                downsample=1,
                autoDownsample=True,
                downsampleMethod="subsample",
                # Note: clipToView=True causes issues with PyQt6 due to
                # autoRangeEnabled() not being accessible on PlotWidget
                clipToView=False,
            )
            self._curves[name] = curve

    def update_series_data(self, name: str, x_data: np.ndarray, y_data: np.ndarray) -> None:
        """Update data for an existing series.

        Args:
            name: Series identifier
            x_data: New X values
            y_data: New Y values
        """
        if name in self._curves:
            self._series_data[name] = (x_data, y_data)
            self._curves[name].setData(x_data, y_data)

    def set_series_visible(self, name: str, visible: bool) -> None:
        """Set visibility of a series.

        Args:
            name: Series identifier
            visible: Whether the series should be visible
        """
        if name in self._curves:
            self._curves[name].setVisible(visible)

    def set_series_color(self, name: str, color: QColor | str) -> None:
        """Set the color of a series.

        Args:
            name: Series identifier
            color: New color
        """
        if name in self._curves:
            if isinstance(color, QColor):
                color = color.name()
            curve = self._curves[name]
            pen = curve.opts["pen"]
            width: int = pen.width() if hasattr(pen, "width") and callable(pen.width) else 1  # type: ignore[union-attr]
            curve.setPen(pg.mkPen(color=color, width=width))

    def set_series_width(self, name: str, width: int) -> None:
        """Set the line width of a series.

        Args:
            name: Series identifier
            width: Line width in pixels
        """
        if name in self._curves:
            curve = self._curves[name]
            pen = curve.opts["pen"]
            color: str = pen.color().name() if hasattr(pen, "color") and callable(pen.color) else "#1f77b4"  # type: ignore[union-attr]
            curve.setPen(pg.mkPen(color=color, width=width))

    def has_series(self, name: str) -> bool:
        """Check if a series exists in the plot.

        Args:
            name: Series identifier

        Returns:
            True if the series exists, False otherwise
        """
        return name in self._curves

    def remove_series(self, name: str) -> None:
        """Remove a series from the plot.

        Args:
            name: Series identifier
        """
        if name in self._curves:
            curve = self._curves.pop(name)
            self._series_data.pop(name, None)
            self._plot_item.removeItem(curve)

    def clear_all(self) -> None:
        """Remove all series from the plot."""
        for name in list(self._curves.keys()):
            self.remove_series(name)
        self._curves.clear()
        self._series_data.clear()
        self.clear_day_boundaries()

    def add_day_boundaries(self, x_data: np.ndarray) -> None:
        """Add vertical dashed lines at day boundaries (midnight).

        Args:
            x_data: X values (Unix timestamps)
        """
        self.clear_day_boundaries()

        if len(x_data) == 0:
            return

        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()
        pen = pg.mkPen(color=colors["day_boundary"], width=1, style=Qt.PenStyle.DashLine)

        # Find day boundaries
        start_ts = float(x_data.min())
        end_ts = float(x_data.max())

        # Get midnight of the first day
        start_dt = datetime.fromtimestamp(start_ts)
        current_day = datetime(start_dt.year, start_dt.month, start_dt.day)

        # Move to next day if we're not exactly at midnight
        if current_day.timestamp() < start_ts:
            current_day += timedelta(days=1)

        # Add lines for each day boundary
        while current_day.timestamp() <= end_ts:
            line = pg.InfiniteLine(
                pos=current_day.timestamp(),
                angle=90,
                movable=False,
                pen=pen,
            )
            self._plot_item.addItem(line, ignoreBounds=True)
            self._day_lines.append(line)

            # Move to next day
            current_day += timedelta(days=1)

    def clear_day_boundaries(self) -> None:
        """Remove all day boundary lines."""
        for line in self._day_lines:
            self._plot_item.removeItem(line)
        self._day_lines.clear()

    def update_day_boundary_theme(self) -> None:
        """Update day boundary line colors for current theme."""
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()
        pen = pg.mkPen(color=colors["day_boundary"], width=1, style=Qt.PenStyle.DashLine)
        for line in self._day_lines:
            line.setPen(pen)

    def auto_range(self) -> None:
        """Reset view to show all data, including hidden series."""
        self._update_y_range()
        # Auto-range X axis only
        self._plot_item.enableAutoRange(axis="x")
        self._plot_item.autoRange()

    def _update_y_range(self) -> None:
        """Update Y axis range to include all series data (visible and hidden)."""
        if not self._series_data:
            return

        y_min = float("inf")
        y_max = float("-inf")

        for _name, (x_data, y_data) in self._series_data.items():
            # Filter out NaN values
            valid_data = y_data[~np.isnan(y_data)]
            if len(valid_data) > 0:
                y_min = min(y_min, float(np.nanmin(valid_data)))
                y_max = max(y_max, float(np.nanmax(valid_data)))

        if y_min != float("inf") and y_max != float("-inf"):
            # Add 5% padding
            padding = (y_max - y_min) * 0.05
            if padding == 0:
                padding = 1.0  # Handle case where all values are the same
            self._plot_item.setYRange(y_min - padding, y_max + padding, padding=0)

    def set_crosshair_visible(self, visible: bool) -> None:
        """Show or hide the crosshair."""
        self._crosshair.set_visible(visible)

    def set_title(self, title: str) -> None:
        """Set the plot title."""
        self._current_title = title
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()
        self._plot_item.setTitle(title, color=colors["title_color"], size="12pt")

    def set_labels(self, x_label: str = "Time Index", y_label: str = "Value") -> None:
        """Set axis labels."""
        theme_manager = ThemeManager.instance()
        colors = theme_manager.get_plot_colors()
        self._plot_item.setLabel("bottom", x_label, color=colors["label_color"])
        self._plot_item.setLabel("left", y_label, color=colors["label_color"])

    def _on_range_changed(self, view_box, ranges) -> None:
        """Handle view range change."""
        x_range = ranges[0]
        self.range_changed.emit(x_range[0], x_range[1])

    def set_time_range(self, start_ts: float, end_ts: float) -> None:
        """Set the visible X-axis range using Unix timestamps.

        Args:
            start_ts: Start time as Unix timestamp
            end_ts: End time as Unix timestamp
        """
        self._plot_item.setXRange(start_ts, end_ts, padding=0)

    def get_current_time_range(self) -> tuple[float, float]:
        """Get current visible X-axis range as Unix timestamps.

        Returns:
            Tuple of (start_timestamp, end_timestamp)
        """
        view_range = self._plot_item.viewRange()
        return view_range[0][0], view_range[0][1]

    def get_data_time_range(self) -> tuple[float, float] | None:
        """Get the full data range (min/max timestamps).

        Returns:
            Tuple of (min_timestamp, max_timestamp) or None if no data
        """
        if not self._series_data:
            return None

        x_min = float("inf")
        x_max = float("-inf")

        for _name, (x_data, _y_data) in self._series_data.items():
            if len(x_data) > 0:
                x_min = min(x_min, float(x_data.min()))
                x_max = max(x_max, float(x_data.max()))

        if x_min == float("inf") or x_max == float("-inf"):
            return None

        return x_min, x_max

    @property
    def plot_widget(self) -> pg.PlotWidget:
        """Get the underlying pyqtgraph PlotWidget."""
        return self._plot_widget

    @property
    def plot_item(self) -> pg.PlotItem:
        """Get the underlying pyqtgraph PlotItem."""
        return self._plot_item
