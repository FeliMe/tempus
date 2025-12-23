"""High-performance plot widget using pyqtgraph."""

from datetime import datetime

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget


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

        # Create crosshair lines
        pen = pg.mkPen(color="#888888", width=1, style=Qt.PenStyle.DashLine)
        self.v_line = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.h_line = pg.InfiniteLine(angle=0, movable=False, pen=pen)

        self.plot_item.addItem(self.v_line, ignoreBounds=True)
        self.plot_item.addItem(self.h_line, ignoreBounds=True)

        # Create label for coordinates
        self.label = pg.TextItem(anchor=(0, 1), color="#aaaaaa")
        self.label.setFont(QFont("Monospace", 9))
        self.plot_item.addItem(self.label, ignoreBounds=True)

        # Connect mouse move
        scene = plot_widget.scene()
        assert scene is not None
        self.proxy = pg.SignalProxy(scene.sigMouseMoved, rateLimit=60, slot=self._on_mouse_moved)  # type: ignore[attr-defined]

        self._visible = True

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
            self.label.setText(f"x={x_str}, y={y:.2f}")

            # Position label in top-left of view
            view_range = self.plot_item.viewRange()
            self.label.setPos(view_range[0][0], view_range[1][1])

    def set_visible(self, visible: bool) -> None:
        """Show or hide the crosshair."""
        self._visible = visible
        self.v_line.setVisible(visible)
        self.h_line.setVisible(visible)
        self.label.setVisible(visible)


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
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the plot widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configure pyqtgraph for dark theme
        pg.setConfigOptions(
            antialias=True,
            background="#1e1e1e",
            foreground="#d4d4d4",
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

        # Enable grid with dark theme styling
        self._plot_item.showGrid(x=True, y=True, alpha=0.3)

        # Configure axis appearance for dark theme
        axis_pen = pg.mkPen(color="#555555", width=1)
        for axis_name in ["bottom", "left", "top", "right"]:
            axis = self._plot_item.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(pg.mkPen(color="#aaaaaa"))

        # Enable mouse interaction (X-axis only for time-series zoom)
        self._plot_item.setMouseEnabled(x=True, y=False)
        # Keep Y-axis auto-ranging to always show full data range
        self._plot_item.enableAutoRange(axis="y")
        self._plot_item.setAutoVisible(y=True)

        # Add crosshair with datetime awareness
        self._crosshair = CrosshairManager(self._plot_widget, self._datetime_axis)

        # Connect range change signal
        self._plot_item.sigRangeChanged.connect(self._on_range_changed)

        # Add legend
        self._legend = self._plot_item.addLegend(offset=(10, 10))
        self._legend.setBrush(pg.mkBrush(color="#2d2d2d"))
        self._legend.setPen(pg.mkPen(color="#555555"))

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

    def remove_series(self, name: str) -> None:
        """Remove a series from the plot.

        Args:
            name: Series identifier
        """
        if name in self._curves:
            curve = self._curves.pop(name)
            self._plot_item.removeItem(curve)

    def clear_all(self) -> None:
        """Remove all series from the plot."""
        for name in list(self._curves.keys()):
            self.remove_series(name)
        self._curves.clear()

    def auto_range(self) -> None:
        """Reset view to show all data."""
        self._plot_item.enableAutoRange()
        self._plot_item.autoRange()

    def set_crosshair_visible(self, visible: bool) -> None:
        """Show or hide the crosshair."""
        self._crosshair.set_visible(visible)

    def set_title(self, title: str) -> None:
        """Set the plot title."""
        self._plot_item.setTitle(title, color="#d4d4d4", size="12pt")

    def set_labels(self, x_label: str = "Time Index", y_label: str = "Value") -> None:
        """Set axis labels."""
        self._plot_item.setLabel("bottom", x_label, color="#aaaaaa")
        self._plot_item.setLabel("left", y_label, color="#aaaaaa")

    def _on_range_changed(self, view_box, ranges) -> None:
        """Handle view range change."""
        x_range = ranges[0]
        self.range_changed.emit(x_range[0], x_range[1])

    @property
    def plot_widget(self) -> pg.PlotWidget:
        """Get the underlying pyqtgraph PlotWidget."""
        return self._plot_widget

    @property
    def plot_item(self) -> pg.PlotItem:
        """Get the underlying pyqtgraph PlotItem."""
        return self._plot_item
