"""Layer manager widget for controlling plot visibility and styling."""

from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QSlider,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


def create_color_icon(color: QColor, size: int = 16) -> QIcon:
    """Create a small colored square icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, size, size, 2, 2)
    painter.end()
    return QIcon(pixmap)


# Default color palette for time-series lines
DEFAULT_COLORS = [
    QColor("#1f77b4"),  # Blue
    QColor("#ff7f0e"),  # Orange
    QColor("#2ca02c"),  # Green
    QColor("#d62728"),  # Red
    QColor("#9467bd"),  # Purple
    QColor("#8c564b"),  # Brown
    QColor("#e377c2"),  # Pink
    QColor("#7f7f7f"),  # Gray
    QColor("#bcbd22"),  # Yellow-green
    QColor("#17becf"),  # Cyan
    QColor("#aec7e8"),  # Light blue
    QColor("#ffbb78"),  # Light orange
    QColor("#98df8a"),  # Light green
    QColor("#ff9896"),  # Light red
    QColor("#c5b0d5"),  # Light purple
]


class LayerItem(QTreeWidgetItem):
    """Tree item representing a data layer (column)."""

    def __init__(self, name: str, color: QColor, parent: QTreeWidget | None = None) -> None:
        super().__init__(parent)
        self.column_name = name
        self._color = color
        self._line_width = 1
        self._visible = True

        # Set up the item
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(0, Qt.CheckState.Checked)
        self.setText(0, name)
        self.setIcon(0, create_color_icon(color))

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, value: QColor) -> None:
        self._color = value
        self.setIcon(0, create_color_icon(value))

    @property
    def line_width(self) -> int:
        return self._line_width

    @line_width.setter
    def line_width(self, value: int) -> None:
        self._line_width = max(1, min(10, value))

    @property
    def visible(self) -> bool:
        return self.checkState(0) == Qt.CheckState.Checked

    @visible.setter
    def visible(self, value: bool) -> None:
        self.setCheckState(0, Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)


class LayerManager(QWidget):
    """Widget for managing plot layers (visibility, color, style, smoothing).

    Signals:
        visibility_changed(str, bool): Emitted when layer visibility changes
        color_changed(str, QColor): Emitted when layer color changes
        line_width_changed(str, int): Emitted when line width changes
        smoothing_changed(int): Emitted when smoothing value changes
    """

    visibility_changed = pyqtSignal(str, bool)
    color_changed = pyqtSignal(str, QColor)
    line_width_changed = pyqtSignal(str, int)
    smoothing_changed = pyqtSignal(int)
    toggle_all_changed = pyqtSignal(bool)  # Emitted when toggle all is clicked

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._layer_items: dict[str, LayerItem] = {}

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Smoothing controls
        smoothing_layout = QHBoxLayout()
        smoothing_label = QLabel("Smoothing:")
        smoothing_label.setStyleSheet("font-weight: bold;")
        smoothing_layout.addWidget(smoothing_label)

        self._smoothing_slider = QSlider(Qt.Orientation.Horizontal)
        self._smoothing_slider.setMinimum(1)
        self._smoothing_slider.setMaximum(500)
        self._smoothing_slider.setValue(1)
        self._smoothing_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._smoothing_slider.setTickInterval(50)
        self._smoothing_slider.valueChanged.connect(self._on_smoothing_changed)
        smoothing_layout.addWidget(self._smoothing_slider, stretch=1)

        self._smoothing_spinbox = QSpinBox()
        self._smoothing_spinbox.setMinimum(1)
        self._smoothing_spinbox.setMaximum(500)
        self._smoothing_spinbox.setValue(1)
        self._smoothing_spinbox.setFixedWidth(60)
        self._smoothing_spinbox.valueChanged.connect(self._on_smoothing_spinbox_changed)
        smoothing_layout.addWidget(self._smoothing_spinbox)

        layout.addLayout(smoothing_layout)

        # Layer header with toggle all button
        layers_header = QHBoxLayout()
        layers_label = QLabel("Layers:")
        layers_label.setStyleSheet("font-weight: bold;")
        layers_header.addWidget(layers_label)
        layers_header.addStretch()

        from PyQt6.QtWidgets import QPushButton

        self._toggle_all_btn = QPushButton("Show All")
        self._toggle_all_btn.setFixedWidth(70)
        self._toggle_all_btn.clicked.connect(self._on_toggle_all)
        layers_header.addWidget(self._toggle_all_btn)
        self._all_visible = False

        layout.addLayout(layers_header)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(False)
        self._tree.setIndentation(0)
        self._tree.itemChanged.connect(self._on_item_changed)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree, stretch=1)

        # Instructions
        instructions = QLabel("Double-click or right-click to change color/width")
        instructions.setStyleSheet("color: #888; font-size: 11px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

    def clear(self) -> None:
        """Clear all layers."""
        self._tree.clear()
        self._layer_items.clear()

    def add_layer(
        self,
        name: str,
        color: QColor | None = None,
        visible: bool = False,
        line_width: int = 1,
    ) -> None:
        """Add a new layer to the manager.

        Args:
            name: Layer/column name
            color: Color for the layer (auto-assigned if None)
            visible: Whether the layer is visible (default False for performance)
            line_width: Line width in pixels (default 1)
        """
        if name in self._layer_items:
            return

        if color is None:
            # Auto-assign color from palette
            color = DEFAULT_COLORS[len(self._layer_items) % len(DEFAULT_COLORS)]

        item = LayerItem(name, color, self._tree)
        item.line_width = line_width
        item.visible = visible
        self._layer_items[name] = item

    def get_layer_config(self, name: str) -> dict[str, Any] | None:
        """Get configuration for a layer.

        Args:
            name: Layer name

        Returns:
            Dict with color, line_width, visible keys, or None if not found
        """
        item = self._layer_items.get(name)
        if item is None:
            return None

        return {
            "color": item.color,
            "line_width": item.line_width,
            "visible": item.visible,
        }

    def get_all_layers(self) -> list[str]:
        """Get list of all layer names."""
        return list(self._layer_items.keys())

    def get_all_configs(self) -> dict[str, dict[str, Any]]:
        """Get configuration for all layers.

        Returns:
            Dictionary mapping layer names to their configuration dicts.
            Each config dict contains 'color' (hex string), 'line_width', and 'visible'.
        """
        configs: dict[str, dict[str, Any]] = {}
        for name, item in self._layer_items.items():
            configs[name] = {
                "color": item.color.name(),  # Convert QColor to hex string
                "line_width": item.line_width,
                "visible": item.visible,
            }
        return configs

    def set_smoothing_value(self, value: int) -> None:
        """Set the smoothing value programmatically.

        Args:
            value: Smoothing window size (1 = no smoothing)
        """
        value = max(1, min(500, value))  # Clamp to valid range
        self._smoothing_slider.blockSignals(True)
        self._smoothing_spinbox.blockSignals(True)
        self._smoothing_slider.setValue(value)
        self._smoothing_spinbox.setValue(value)
        self._smoothing_slider.blockSignals(False)
        self._smoothing_spinbox.blockSignals(False)

    @property
    def smoothing_value(self) -> int:
        """Get current smoothing window size."""
        return self._smoothing_slider.value()

    def _on_smoothing_changed(self, value: int) -> None:
        """Handle smoothing slider change."""
        self._smoothing_spinbox.blockSignals(True)
        self._smoothing_spinbox.setValue(value)
        self._smoothing_spinbox.blockSignals(False)
        self.smoothing_changed.emit(value)

    def _on_smoothing_spinbox_changed(self, value: int) -> None:
        """Handle smoothing spinbox change."""
        self._smoothing_slider.blockSignals(True)
        self._smoothing_slider.setValue(value)
        self._smoothing_slider.blockSignals(False)
        self.smoothing_changed.emit(value)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item checkbox change."""
        if not isinstance(item, LayerItem):
            return

        self.visibility_changed.emit(item.column_name, item.visible)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle double-click to change color."""
        if not isinstance(item, LayerItem):
            return

        self._change_layer_color(item)

    def _show_context_menu(self, position) -> None:
        """Show context menu for layer customization."""
        item = self._tree.itemAt(position)
        if not isinstance(item, LayerItem):
            return

        menu = QMenu(self)

        # Color action
        color_action = menu.addAction("Change Color...")
        if color_action is not None:
            color_action.triggered.connect(lambda: self._change_layer_color(item))

        # Line width submenu
        width_menu = menu.addMenu("Line Width")
        if width_menu is not None:
            for width in [1, 2, 3, 4, 5]:
                action = width_menu.addAction(f"{width} px")
                if action is not None:
                    action.setCheckable(True)
                    action.setChecked(item.line_width == width)
                    action.triggered.connect(lambda checked, w=width: self._change_line_width(item, w))

        menu.addSeparator()

        # Visibility toggle
        if item.visible:
            hide_action = menu.addAction("Hide")
            if hide_action is not None:
                hide_action.triggered.connect(lambda: self._set_visibility(item, False))
        else:
            show_action = menu.addAction("Show")
            if show_action is not None:
                show_action.triggered.connect(lambda: self._set_visibility(item, True))

        menu.exec(self._tree.mapToGlobal(position))

    def _change_layer_color(self, item: LayerItem) -> None:
        """Open color dialog to change layer color."""
        color = QColorDialog.getColor(item.color, self, f"Select color for {item.column_name}")
        if color.isValid():
            item.color = color
            self.color_changed.emit(item.column_name, color)

    def _change_line_width(self, item: LayerItem, width: int) -> None:
        """Change line width for a layer."""
        item.line_width = width
        self.line_width_changed.emit(item.column_name, width)

    def _set_visibility(self, item: LayerItem, visible: bool) -> None:
        """Set layer visibility."""
        item.visible = visible
        # itemChanged signal will emit visibility_changed

    def _on_toggle_all(self) -> None:
        """Toggle visibility of all layers."""
        self._all_visible = not self._all_visible
        self._toggle_all_btn.setText("Hide All" if self._all_visible else "Show All")

        # Block signals to avoid emitting for each item
        self._tree.blockSignals(True)
        for item in self._layer_items.values():
            item.visible = self._all_visible
        self._tree.blockSignals(False)

        # Emit single signal for batch update
        self.toggle_all_changed.emit(self._all_visible)

    def set_all_visible(self, visible: bool) -> None:
        """Set visibility of all layers programmatically.

        Args:
            visible: Whether all layers should be visible
        """
        self._all_visible = visible
        self._toggle_all_btn.setText("Hide All" if visible else "Show All")

        self._tree.blockSignals(True)
        for item in self._layer_items.values():
            item.visible = visible
        self._tree.blockSignals(False)
