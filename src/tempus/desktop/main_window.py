"""Main window with dock layout for the desktop application."""

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QKeySequence
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
from tempus.desktop.widgets.layer_manager import LayerManager
from tempus.desktop.widgets.plot_widget import TimeSeriesPlotWidget


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

        # Set up the UI
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        # Set window properties
        self.setWindowTitle("Tempus - Time Series Viewer")
        self.setMinimumSize(1200, 800)

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

        toggle_crosshair_action = QAction("Toggle &Crosshair", self)
        toggle_crosshair_action.setShortcut(QKeySequence("Ctrl+H"))
        toggle_crosshair_action.setCheckable(True)
        toggle_crosshair_action.setChecked(True)
        toggle_crosshair_action.triggered.connect(self._on_toggle_crosshair)
        view_menu.addAction(toggle_crosshair_action)
        self._toggle_crosshair_action = toggle_crosshair_action

        view_menu.addSeparator()

        toggle_layers_action = self._layer_dock.toggleViewAction()
        if toggle_layers_action is not None:
            toggle_layers_action.setText("&Layer Manager")
            toggle_layers_action.setShortcut(QKeySequence("Ctrl+L"))
            view_menu.addAction(toggle_layers_action)

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

        # Layer manager signals
        self._layer_manager.visibility_changed.connect(self._on_visibility_changed)
        self._layer_manager.color_changed.connect(self._on_color_changed)
        self._layer_manager.line_width_changed.connect(self._on_line_width_changed)
        self._layer_manager.smoothing_changed.connect(self._on_smoothing_changed)
        self._layer_manager.toggle_all_changed.connect(self._on_toggle_all)

    def _on_open_file(self) -> None:
        """Handle file open action."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")

        if filepath:
            self._load_file(filepath)

    def _load_file(self, filepath: str) -> None:
        """Load a CSV file."""
        self._statusbar.showMessage(f"Loading {Path(filepath).name}...")

        # Clear existing data
        self._plot_widget.clear_all()
        self._layer_manager.clear()

        # Load new data
        if self._model.load_csv(filepath):
            self._statusbar.showMessage(f"Loaded {self._model.filename} - {self._model.row_count:,} rows")

    def _on_data_loaded(self, filename: str) -> None:
        """Handle data loaded event."""
        # Add layers to manager and plot
        time_values = self._model.time_values
        if time_values is None:
            return

        for column in self._model.numeric_columns:
            # Add to layer manager (auto-assigns color)
            self._layer_manager.add_layer(column)

            # Get configuration from layer manager
            config = self._layer_manager.get_layer_config(column)
            if config is None:
                continue

            # Get data
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
        self._plot_widget.set_series_visible(column, visible)

    def _on_toggle_all(self, visible: bool) -> None:
        """Handle toggle all layers visibility."""
        for column in self._model.numeric_columns:
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

        # Update all series with smoothed data
        for column in self._model.numeric_columns:
            y_data = self._model.get_smoothed_data(column, window)
            if y_data is not None:
                self._plot_widget.update_series_data(column, time_values, y_data)

    def _on_reset_view(self) -> None:
        """Reset plot view to show all data."""
        self._plot_widget.auto_range()

    def _on_toggle_crosshair(self, checked: bool) -> None:
        """Toggle crosshair visibility."""
        self._plot_widget.set_crosshair_visible(checked)

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
