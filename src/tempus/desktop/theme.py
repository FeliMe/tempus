"""Theme management for the desktop application."""

from enum import Enum
from typing import cast

import pyqtgraph as pg
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class Theme(Enum):
    """Available application themes."""

    LIGHT = "light"
    DARK = "dark"


# Theme color definitions
THEME_COLORS = {
    Theme.LIGHT: {
        # Application colors
        "window": QColor(248, 248, 248),
        "window_text": QColor(30, 30, 30),
        "base": QColor(255, 255, 255),
        "alternate_base": QColor(245, 245, 245),
        "tooltip_base": QColor(255, 255, 255),
        "tooltip_text": QColor(30, 30, 30),
        "text": QColor(30, 30, 30),
        "button": QColor(240, 240, 240),
        "button_text": QColor(30, 30, 30),
        "highlight": QColor(0, 120, 215),
        "highlighted_text": QColor(255, 255, 255),
        "link": QColor(0, 120, 215),
        "disabled_text": QColor(160, 160, 160),
        # Plot colors
        "plot_background": "#ffffff",
        "plot_foreground": "#1e1e1e",
        "plot_grid_alpha": 0.2,
        "axis_pen": "#cccccc",
        "axis_text": "#555555",
        "crosshair_pen": "#888888",
        "crosshair_label": "#555555",
        "legend_background": "#f5f5f5",
        "legend_border": "#cccccc",
        "legend_text": "#1e1e1e",
        "title_color": "#1e1e1e",
        "label_color": "#555555",
        "day_boundary": "#cccccc",
    },
    Theme.DARK: {
        # Application colors
        "window": QColor(30, 30, 30),
        "window_text": QColor(212, 212, 212),
        "base": QColor(25, 25, 25),
        "alternate_base": QColor(30, 30, 30),
        "tooltip_base": QColor(45, 45, 45),
        "tooltip_text": QColor(212, 212, 212),
        "text": QColor(212, 212, 212),
        "button": QColor(61, 61, 61),
        "button_text": QColor(212, 212, 212),
        "highlight": QColor(61, 174, 233),
        "highlighted_text": QColor(0, 0, 0),
        "link": QColor(61, 174, 233),
        "disabled_text": QColor(127, 127, 127),
        # Plot colors
        "plot_background": "#1e1e1e",
        "plot_foreground": "#d4d4d4",
        "plot_grid_alpha": 0.3,
        "axis_pen": "#555555",
        "axis_text": "#aaaaaa",
        "crosshair_pen": "#888888",
        "crosshair_label": "#aaaaaa",
        "legend_background": "#2d2d2d",
        "legend_border": "#555555",
        "legend_text": "#d4d4d4",
        "title_color": "#d4d4d4",
        "label_color": "#aaaaaa",
        "day_boundary": "#555555",
    },
}

# Theme stylesheets
THEME_STYLESHEETS = {
    Theme.LIGHT: """
        QToolTip {
            color: #1e1e1e;
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 4px;
        }
        QMenuBar {
            background-color: #f5f5f5;
            color: #1e1e1e;
        }
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        QMenu {
            background-color: #ffffff;
            color: #1e1e1e;
            border: 1px solid #cccccc;
        }
        QMenu::item:selected {
            background-color: #0078d7;
            color: #ffffff;
        }
        QDockWidget {
            color: #1e1e1e;
        }
        QDockWidget::title {
            background-color: #f0f0f0;
            padding: 6px;
        }
        QTreeWidget {
            background-color: #ffffff;
            color: #1e1e1e;
            border: 1px solid #cccccc;
        }
        QTreeWidget::item:selected {
            background-color: #0078d7;
            color: #ffffff;
        }
        QSlider::groove:horizontal {
            background: #cccccc;
            height: 4px;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #0078d7;
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        QSpinBox {
            background-color: #ffffff;
            color: #1e1e1e;
            border: 1px solid #cccccc;
            padding: 2px;
        }
        QPushButton {
            background-color: #e0e0e0;
            color: #1e1e1e;
            border: 1px solid #cccccc;
            padding: 6px 12px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #0078d7;
            color: #ffffff;
        }
        QStatusBar {
            background-color: #f5f5f5;
            color: #555555;
        }
        QToolBar {
            background-color: #f5f5f5;
            border: none;
            spacing: 6px;
            padding: 4px;
        }
        QLabel {
            color: #1e1e1e;
        }
    """,
    Theme.DARK: """
        QToolTip {
            color: #d4d4d4;
            background-color: #2d2d2d;
            border: 1px solid #3f3f3f;
            padding: 4px;
        }
        QMenuBar {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
        }
        QMenu::item:selected {
            background-color: #3daee9;
        }
        QDockWidget {
            color: #d4d4d4;
        }
        QDockWidget::title {
            background-color: #2d2d2d;
            padding: 6px;
        }
        QTreeWidget {
            background-color: #252525;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
        }
        QTreeWidget::item:selected {
            background-color: #3daee9;
        }
        QSlider::groove:horizontal {
            background: #3f3f3f;
            height: 4px;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #3daee9;
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        QSpinBox {
            background-color: #252525;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
            padding: 2px;
        }
        QPushButton {
            background-color: #3d3d3d;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
            padding: 6px 12px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        QPushButton:pressed {
            background-color: #3daee9;
        }
        QStatusBar {
            background-color: #1e1e1e;
            color: #888888;
        }
        QToolBar {
            background-color: #1e1e1e;
            border: none;
            spacing: 6px;
            padding: 4px;
        }
        QLabel {
            color: #d4d4d4;
        }
    """,
}


class ThemeManager(QObject):
    """Manages application theming."""

    theme_changed = pyqtSignal(Theme)

    _instance: "ThemeManager | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._current_theme = Theme.LIGHT  # Default to light mode

    @classmethod
    def instance(cls) -> "ThemeManager":
        """Get the singleton instance of ThemeManager."""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    @property
    def current_theme(self) -> Theme:
        """Get the current theme."""
        return self._current_theme

    def set_theme(self, theme: Theme) -> None:
        """Set the application theme.

        Args:
            theme: The theme to apply
        """
        if theme == self._current_theme:
            return

        self._current_theme = theme
        self._apply_theme(theme)
        self.theme_changed.emit(theme)

    def toggle_theme(self) -> Theme:
        """Toggle between light and dark themes.

        Returns:
            The new theme after toggling
        """
        new_theme = Theme.DARK if self._current_theme == Theme.LIGHT else Theme.LIGHT
        self.set_theme(new_theme)
        return new_theme

    def apply_initial_theme(self) -> None:
        """Apply the initial theme without emitting signals."""
        self._apply_theme(self._current_theme)

    def _apply_theme(self, theme: Theme) -> None:
        """Apply theme to the application."""
        from PyQt6.QtCore import Qt

        app = QApplication.instance()
        if app is None:
            return

        colors = THEME_COLORS[theme]

        # Create and apply palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, cast(QColor, colors["window"]))
        palette.setColor(QPalette.ColorRole.WindowText, cast(QColor, colors["window_text"]))
        palette.setColor(QPalette.ColorRole.Base, cast(QColor, colors["base"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, cast(QColor, colors["alternate_base"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, cast(QColor, colors["tooltip_base"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, cast(QColor, colors["tooltip_text"]))
        palette.setColor(QPalette.ColorRole.Text, cast(QColor, colors["text"]))
        palette.setColor(QPalette.ColorRole.Button, cast(QColor, colors["button"]))
        palette.setColor(QPalette.ColorRole.ButtonText, cast(QColor, colors["button_text"]))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, cast(QColor, colors["link"]))
        palette.setColor(QPalette.ColorRole.Highlight, cast(QColor, colors["highlight"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, cast(QColor, colors["highlighted_text"]))

        # Disabled colors
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, cast(QColor, colors["disabled_text"])
        )
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, cast(QColor, colors["disabled_text"]))
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, cast(QColor, colors["disabled_text"])
        )

        app.setPalette(palette)  # type: ignore[union-attr]
        app.setStyleSheet(THEME_STYLESHEETS[theme])  # type: ignore[union-attr]

        # Configure pyqtgraph colors
        pg.setConfigOptions(
            background=colors["plot_background"],
            foreground=colors["plot_foreground"],
        )

    def get_color(self, key: str) -> str | QColor | float:
        """Get a theme color by key.

        Args:
            key: The color key from THEME_COLORS

        Returns:
            The color value for the current theme
        """
        return THEME_COLORS[self._current_theme][key]

    def get_plot_colors(self) -> dict:
        """Get all plot-related colors for the current theme.

        Returns:
            Dictionary with plot color values
        """
        colors = THEME_COLORS[self._current_theme]
        return {
            "background": colors["plot_background"],
            "foreground": colors["plot_foreground"],
            "grid_alpha": colors["plot_grid_alpha"],
            "axis_pen": colors["axis_pen"],
            "axis_text": colors["axis_text"],
            "crosshair_pen": colors["crosshair_pen"],
            "crosshair_label": colors["crosshair_label"],
            "legend_background": colors["legend_background"],
            "legend_border": colors["legend_border"],
            "legend_text": colors["legend_text"],
            "title_color": colors["title_color"],
            "label_color": colors["label_color"],
            "day_boundary": colors["day_boundary"],
        }
