#!/usr/bin/env python3
"""Entry point for the Tempus desktop application.

A high-performance desktop GUI for visualizing large time-series datasets.
Uses PyQt6 and pyqtgraph for smooth interaction with millions of data points.

Usage:
    uv run python -m tempus.desktop_app [csv_file]

    Or with the script:
    uv run tempus-desktop [csv_file]
"""

import os
import sys
from pathlib import Path

# Apply UI scale factor BEFORE importing QApplication
os.environ["QT_SCALE_FACTOR"] = "1.5"

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from tempus.desktop.theme import ThemeManager


def main() -> int:
    """Main entry point for the application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Tempus")
    app.setOrganizationName("Tempus")
    app.setApplicationVersion("0.1.0")

    # Apply initial theme (light mode by default)
    theme_manager = ThemeManager.instance()
    theme_manager.apply_initial_theme()

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
