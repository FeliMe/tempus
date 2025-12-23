#!/usr/bin/env python3
"""Entry point for the Tempus desktop application.

A high-performance desktop GUI for visualizing large time-series datasets.
Uses PyQt6 and pyqtgraph for smooth interaction with millions of data points.

Usage:
    uv run python -m tempus.desktop_app [csv_file]

    Or with the script:
    uv run tempus-desktop [csv_file]
"""

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Try to import qdarktheme for a modern dark appearance
try:
    import qdarktheme  # type: ignore[import-not-found]

    HAS_DARK_THEME = True
except ImportError:
    try:
        # Alternative package name
        import pyqtdarktheme as qdarktheme  # type: ignore[import-not-found]

        HAS_DARK_THEME = True
    except ImportError:
        HAS_DARK_THEME = False


def setup_dark_theme(app: QApplication) -> None:
    """Apply dark theme to the application.

    Uses qdarktheme if available, falls back to custom palette otherwise.
    """
    if HAS_DARK_THEME:
        # Use qdarktheme for a polished dark appearance
        qdarktheme.setup_theme(
            theme="dark",
            custom_colors={
                "[dark]": {
                    "primary": "#3daee9",
                    "background": "#1e1e1e",
                    "border": "#3f3f3f",
                    "background>popup": "#2d2d2d",
                }
            },
        )
    else:
        # Fallback: Apply a basic dark palette
        from PyQt6.QtGui import QColor, QPalette

        palette = QPalette()

        # Dark colors
        dark_color = QColor(30, 30, 30)
        disabled_color = QColor(127, 127, 127)
        text_color = QColor(212, 212, 212)
        highlight_color = QColor(61, 174, 233)

        palette.setColor(QPalette.ColorRole.Window, dark_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, dark_color)
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, dark_color)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, highlight_color)
        palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_color)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color)

        app.setPalette(palette)

        # Apply some additional styling via stylesheet
        app.setStyleSheet("""
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
        """)


def main() -> int:
    """Main entry point for the application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Tempus")
    app.setOrganizationName("Tempus")
    app.setApplicationVersion("0.1.0")

    # Apply dark theme
    setup_dark_theme(app)

    # Import main window here to avoid circular imports and ensure theme is applied first
    from tempus.desktop.main_window import MainWindow

    # Create and show main window
    window = MainWindow()
    window.show()

    # Load file from command line if provided
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
        if filepath.exists():
            window.load_file_on_startup(str(filepath))

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
