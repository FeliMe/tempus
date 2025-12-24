"""Main window with dock layout for the desktop application."""

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QCloseEvent, QColor, QKeySequence
from PyQt6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QToolBar,
)

from tempus.desktop.model.data_model import DataModel
from tempus.desktop.theme import Theme, ThemeManager
from tempus.desktop.widgets.datetime_range_dialog import DateTimeRangeDialog
from tempus.desktop.widgets.layer_manager import LayerManager
from tempus.desktop.widgets.plot_widget import TimeSeriesPlotWidget
from tempus.utils.config_manager import ConfigManager


class MainWindow(QMainWindow):
    """Main application window with dock-based layout.

    Layout:
    - Center: Time-series plot widget
    - Left Dock: Layer manager (visibility, colors, smoothing)
    """

    def __init__(self) -> None:
        super().__init__()

        # Initialize model
        self._model = DataModel(self)
        self._current_smoothing = 1
        self._current_filepath: str | None = None

        # Get managers
        self._theme_manager = ThemeManager.instance()
        self._config_manager = ConfigManager.instance()

        # Debounce timer for config saving (avoids disk writes on every UI change)
        self._config_save_timer = QTimer()
        self._config_save_timer.setSingleShot(True)
        self._config_save_timer.setInterval(500)  # 500ms debounce
        self._config_save_timer.timeout.connect(self._do_save_config)

        # Set up the UI
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        # Set window properties
        self.setWindowTitle("Tempus - Time Series Viewer")

        # Restore geometry if available (TODO: implement settings persistence)

    def _setup_ui(self) -> None:
        """Set up the main UI components."""
        # Create central plot widget
        self._plot_widget = TimeSeriesPlotWidget(self)
        self.setCentralWidget(self._plot_widget)

        # Create layer manager dock
        self._layer_manager = LayerManager(self)
        self._layer_dock = QDockWidget("Layer Manager", self)
        self._layer_dock.setWidget(self._layer_manager)
        self._layer_dock.setMinimumWidth(250)
        self._layer_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._layer_dock)

    def _setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # File menu
        file_menu = menubar.addMenu("&File")
        assert file_menu is not None

        open_action = QAction("&Open CSV...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        assert view_menu is not None

        reset_view_action = QAction("&Reset View", self)
        reset_view_action.setShortcut(QKeySequence("Ctrl+R"))
        reset_view_action.triggered.connect(self._on_reset_view)
        view_menu.addAction(reset_view_action)

        set_time_range_action = QAction("Set &Time Range...", self)
        set_time_range_action.setShortcut(QKeySequence("Ctrl+G"))
        set_time_range_action.triggered.connect(self._on_set_time_range)
        view_menu.addAction(set_time_range_action)

        view_menu.addSeparator()

        toggle_crosshair_action = QAction("Toggle &Crosshair", self)
        toggle_crosshair_action.setShortcut(QKeySequence("Ctrl+H"))
        toggle_crosshair_action.setCheckable(True)
        toggle_crosshair_action.setChecked(True)
        toggle_crosshair_action.triggered.connect(self._on_toggle_crosshair)
        view_menu.addAction(toggle_crosshair_action)
        self._toggle_crosshair_action = toggle_crosshair_action

        view_menu.addSeparator()

        # Theme toggle action
        toggle_theme_action = QAction("&Dark Mode", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.setCheckable(True)
        toggle_theme_action.setChecked(self._theme_manager.current_theme == Theme.DARK)
        toggle_theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(toggle_theme_action)
        self._toggle_theme_action = toggle_theme_action

        view_menu.addSeparator()

        toggle_layers_action = self._layer_dock.toggleViewAction()
        if toggle_layers_action is not None:
            toggle_layers_action.setText("&Layer Manager")
            toggle_layers_action.setShortcut(QKeySequence("Ctrl+L"))
            view_menu.addAction(toggle_layers_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        assert settings_menu is not None

        reset_settings_action = QAction("&Reset File Settings...", self)
        reset_settings_action.triggered.connect(self._on_reset_settings)
        settings_menu.addAction(reset_settings_action)
        self._reset_settings_action = reset_settings_action

        # Help menu
        help_menu = menubar.addMenu("&Help")
        assert help_menu is not None

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open file action
        open_action = QAction("Open", self)
        open_action.setToolTip("Open CSV file (Ctrl+O)")
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Reset view action
        reset_action = QAction("Reset View", self)
        reset_action.setToolTip("Reset plot view to show all data (Ctrl+R)")
        reset_action.triggered.connect(self._on_reset_view)
        toolbar.addAction(reset_action)

        toolbar.addSeparator()

        # Theme toggle action
        theme_action = QAction("Toggle Theme", self)
        theme_action.setToolTip("Switch between light and dark mode (Ctrl+T)")
        theme_action.triggered.connect(self._on_toggle_theme)
        toolbar.addAction(theme_action)

    def _setup_statusbar(self) -> None:
        """Set up the status bar."""
        self._statusbar = QStatusBar(self)
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Ready - Open a CSV file to begin")

    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Model signals
        self._model.data_loaded.connect(self._on_data_loaded)
        self._model.data_cleared.connect(self._on_data_cleared)
        self._model.error_occurred.connect(self._on_error)

        # Layer manager signals - UI updates
        self._layer_manager.visibility_changed.connect(self._on_visibility_changed)
        self._layer_manager.color_changed.connect(self._on_color_changed)
        self._layer_manager.line_width_changed.connect(self._on_line_width_changed)
        self._layer_manager.smoothing_changed.connect(self._on_smoothing_changed)
        self._layer_manager.toggle_all_changed.connect(self._on_toggle_all)

        # Layer manager signals - Config persistence (save on any change)
        self._layer_manager.visibility_changed.connect(lambda *_: self._on_config_changed())
        self._layer_manager.color_changed.connect(lambda *_: self._on_config_changed())
        self._layer_manager.line_width_changed.connect(lambda *_: self._on_config_changed())
        self._layer_manager.smoothing_changed.connect(lambda *_: self._on_config_changed())
        self._layer_manager.toggle_all_changed.connect(lambda *_: self._on_config_changed())

    def _on_open_file(self) -> None:
        """Handle file open action."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")

        if filepath:
            self._load_file(filepath)

    def _load_file(self, filepath: str) -> None:
        """Load a CSV file."""
        self._statusbar.showMessage(f"Loading {Path(filepath).name}...")

        # Save current file config before loading new file
        self._save_current_config()

        # Clear existing data
        self._plot_widget.clear_all()
        self._layer_manager.clear()

        # Track current file
        self._current_filepath = filepath

        # Load new data
        if self._model.load_csv(filepath):
            self._statusbar.showMessage(f"Loaded {self._model.filename} - {self._model.row_count:,} rows")

    def _on_data_loaded(self, filename: str) -> None:
        """Handle data loaded event."""
        # Add layers to manager and plot
        time_values = self._model.time_values
        if time_values is None:
            return

        # Check for saved configuration
        saved_config = None
        if self._current_filepath:
            saved_config = self._config_manager.get_file_config(self._current_filepath)

        # Apply saved smoothing if available
        if saved_config and "smoothing" in saved_config:
            saved_smoothing = saved_config["smoothing"]
            self._layer_manager.set_smoothing_value(saved_smoothing)
            self._current_smoothing = saved_smoothing

        for column in self._model.numeric_columns:
            # Check if we have saved config for this layer
            layer_saved = None
            if saved_config and "layers" in saved_config:
                layer_saved = saved_config["layers"].get(column)

            if layer_saved:
                # Apply saved configuration
                color = QColor(layer_saved.get("color", "#1f77b4"))
                visible = layer_saved.get("visible", True)
                line_width = layer_saved.get("line_width", 1)
                self._layer_manager.add_layer(
                    column,
                    color=color,
                    visible=visible,
                    line_width=line_width,
                )
            else:
                # Add with default configuration (auto-assigns color)
                self._layer_manager.add_layer(column)

            # Get configuration from layer manager
            config = self._layer_manager.get_layer_config(column)
            if config is None:
                continue

            # Only add visible series to the plot for performance
            # Hidden series are added lazily when they become visible
            if not config["visible"]:
                continue

            # Get data (apply saved smoothing if any)
            if self._current_smoothing > 1:
                y_data = self._model.get_smoothed_data(column, self._current_smoothing)
            else:
                y_data = self._model.get_column_data(column)
            if y_data is None:
                continue

            # Add to plot
            self._plot_widget.add_series(
                name=column,
                x_data=time_values,
                y_data=y_data,
                color=config["color"],
                width=config["line_width"],
            )

        # Add day boundary lines
        self._plot_widget.add_day_boundaries(time_values)

        # Set plot title
        self._plot_widget.set_title(filename)

        # Auto-range to show all data
        self._plot_widget.auto_range()

    def _on_data_cleared(self) -> None:
        """Handle data cleared event."""
        self._plot_widget.clear_all()
        self._layer_manager.clear()
        self._statusbar.showMessage("Ready - Open a CSV file to begin")

    def _on_error(self, message: str) -> None:
        """Handle error event."""
        QMessageBox.critical(self, "Error", message)
        self._statusbar.showMessage("Error: " + message)

    def _on_visibility_changed(self, column: str, visible: bool) -> None:
        """Handle layer visibility change."""
        if visible:
            # Lazily add the series if it doesn't exist yet
            self._ensure_series_added(column)
        self._plot_widget.set_series_visible(column, visible)

    def _ensure_series_added(self, column: str) -> None:
        """Ensure a series is added to the plot (lazy loading for performance)."""
        # Check if series already exists in plot
        if self._plot_widget.has_series(column):
            return

        time_values = self._model.time_values
        if time_values is None:
            return

        config = self._layer_manager.get_layer_config(column)
        if config is None:
            return

        # Get data with current smoothing
        if self._current_smoothing > 1:
            y_data = self._model.get_smoothed_data(column, self._current_smoothing)
        else:
            y_data = self._model.get_column_data(column)
        if y_data is None:
            return

        # Add to plot
        self._plot_widget.add_series(
            name=column,
            x_data=time_values,
            y_data=y_data,
            color=config["color"],
            width=config["line_width"],
        )

    def _on_toggle_all(self, visible: bool) -> None:
        """Handle toggle all layers visibility."""
        for column in self._model.numeric_columns:
            if visible:
                # Lazily add series if showing
                self._ensure_series_added(column)
            self._plot_widget.set_series_visible(column, visible)

    def _on_color_changed(self, column: str, color: QColor) -> None:
        """Handle layer color change."""
        self._plot_widget.set_series_color(column, color)

    def _on_line_width_changed(self, column: str, width: int) -> None:
        """Handle line width change."""
        self._plot_widget.set_series_width(column, width)

    def _on_smoothing_changed(self, window: int) -> None:
        """Handle smoothing value change."""
        self._current_smoothing = window

        time_values = self._model.time_values
        if time_values is None:
            return

        # Update only series that exist in the plot (visible ones)
        for column in self._model.numeric_columns:
            if not self._plot_widget.has_series(column):
                continue
            y_data = self._model.get_smoothed_data(column, window)
            if y_data is not None:
                self._plot_widget.update_series_data(column, time_values, y_data)

    def _on_reset_view(self) -> None:
        """Reset plot view to show all data."""
        self._plot_widget.auto_range()

    def _on_set_time_range(self) -> None:
        """Open dialog to set a custom time range."""
        # Get current view range
        current_start, current_end = self._plot_widget.get_current_time_range()

        # Get full data range
        data_range = self._plot_widget.get_data_time_range()
        data_start = data_range[0] if data_range else None
        data_end = data_range[1] if data_range else None

        # Show dialog
        dialog = DateTimeRangeDialog(
            parent=self,
            current_start=current_start,
            current_end=current_end,
            data_start=data_start,
            data_end=data_end,
        )

        if dialog.exec() == DateTimeRangeDialog.DialogCode.Accepted:
            start_ts, end_ts = dialog.get_range()
            self._plot_widget.set_time_range(start_ts, end_ts)
            self._statusbar.showMessage("Time range set")

    def _on_toggle_crosshair(self, checked: bool) -> None:
        """Toggle crosshair visibility."""
        self._plot_widget.set_crosshair_visible(checked)

    def _on_toggle_theme(self, checked: bool | None = None) -> None:
        """Toggle between light and dark theme."""
        new_theme = self._theme_manager.toggle_theme()
        # Update the menu action check state
        self._toggle_theme_action.setChecked(new_theme == Theme.DARK)

    def _on_reset_settings(self) -> None:
        """Show confirmation dialog and reset settings for the current file."""
        if not self._current_filepath:
            QMessageBox.information(
                self,
                "No File Loaded",
                "No file is currently loaded. Open a file first to reset its settings.",
            )
            return

        filename = Path(self._current_filepath).name
        reply = QMessageBox.warning(
            self,
            "Reset File Settings",
            f"This will reset all saved settings for:\n\n"
            f"{filename}\n\n"
            f"Including:\n"
            f"• Layer colors and visibility\n"
            f"• Line widths\n"
            f"• Smoothing preferences\n\n"
            f"Settings for other files will not be affected.\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._config_manager.remove_file_config(self._current_filepath)
            self._statusbar.showMessage(f"Settings reset for {filename}")

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Tempus",
            "<h2>Tempus Time Series Viewer</h2>"
            "<p>Version 0.1.0</p>"
            "<p>A high-performance desktop application for visualizing "
            "large time-series datasets.</p>"
            "<p>Built with PyQt6 and pyqtgraph for smooth interaction "
            "with millions of data points.</p>",
        )

    def load_file_on_startup(self, filepath: str) -> None:
        """Load a file on application startup.

        Args:
            filepath: Path to the CSV file to load
        """
        self._load_file(filepath)

    def _save_current_config(self) -> None:
        """Save the current layer configuration to the config manager."""
        if self._current_filepath is None:
            return

        # Get all layer configurations
        layer_configs = self._layer_manager.get_all_configs()
        if not layer_configs:
            return

        # Build the full config dict
        config_dict = {
            "layers": layer_configs,
            "smoothing": self._layer_manager.smoothing_value,
        }

        # Save to config manager
        self._config_manager.save_file_config(self._current_filepath, config_dict)

    def _on_config_changed(self) -> None:
        """Handle any configuration change by scheduling a debounced save."""
        # Debounce config saves to avoid disk I/O on every UI interaction
        self._config_save_timer.start()

    def _do_save_config(self) -> None:
        """Actually save the config after debounce delay."""
        self._save_current_config()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        """Handle window close event to save configuration.

        Args:
            a0: The close event
        """
        # Save current configuration before closing
        self._save_current_config()
        if a0:
            a0.accept()
