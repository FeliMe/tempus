"""Dialog for selecting a date/time range."""

from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class DateTimeRangeDialog(QDialog):
    """Dialog for selecting a start and end date/time range.

    The dialog allows users to:
    - Select start and end datetime using calendar popups
    - Optionally reset to the full data range
    - Validates that start < end
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        current_start: float | None = None,
        current_end: float | None = None,
        data_start: float | None = None,
        data_end: float | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            parent: Parent widget
            current_start: Current view start as Unix timestamp
            current_end: Current view end as Unix timestamp
            data_start: Full data range start as Unix timestamp
            data_end: Full data range end as Unix timestamp
        """
        super().__init__(parent)

        self._data_start = data_start
        self._data_end = data_end

        self._setup_ui(current_start, current_end, data_start, data_end)

    def _setup_ui(
        self,
        current_start: float | None,
        current_end: float | None,
        data_start: float | None,
        data_end: float | None,
    ) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("Set Time Range")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel("Select the time range to display:")
        layout.addWidget(info_label)

        # Form layout for datetime inputs
        form_layout = QFormLayout()

        # Start datetime
        self._start_edit = QDateTimeEdit()
        self._start_edit.setCalendarPopup(True)
        self._start_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        form_layout.addRow("Start:", self._start_edit)

        # End datetime
        self._end_edit = QDateTimeEdit()
        self._end_edit.setCalendarPopup(True)
        self._end_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        form_layout.addRow("End:", self._end_edit)

        layout.addLayout(form_layout)

        # Set datetime limits based on data range
        if data_start is not None and data_end is not None:
            min_dt = QDateTime.fromSecsSinceEpoch(int(data_start))
            max_dt = QDateTime.fromSecsSinceEpoch(int(data_end))
            self._start_edit.setDateTimeRange(min_dt, max_dt)
            self._end_edit.setDateTimeRange(min_dt, max_dt)

        # Set current values
        if current_start is not None:
            self._start_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(current_start)))
        elif data_start is not None:
            self._start_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(data_start)))

        if current_end is not None:
            self._end_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(current_end)))
        elif data_end is not None:
            self._end_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(data_end)))

        # Full range checkbox
        self._full_range_checkbox = QCheckBox("Use full data range")
        self._full_range_checkbox.stateChanged.connect(self._on_full_range_changed)
        layout.addWidget(self._full_range_checkbox)

        # Error label (hidden by default)
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect datetime changes to validation
        self._start_edit.dateTimeChanged.connect(self._validate)
        self._end_edit.dateTimeChanged.connect(self._validate)

    def _on_full_range_changed(self, state: int) -> None:
        """Handle full range checkbox change."""
        is_checked = state == Qt.CheckState.Checked.value

        self._start_edit.setEnabled(not is_checked)
        self._end_edit.setEnabled(not is_checked)

        if is_checked and self._data_start is not None and self._data_end is not None:
            self._start_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(self._data_start)))
            self._end_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(self._data_end)))

        self._validate()

    def _validate(self) -> bool:
        """Validate that start < end.

        Returns:
            True if valid, False otherwise
        """
        start_ts = self._start_edit.dateTime().toSecsSinceEpoch()
        end_ts = self._end_edit.dateTime().toSecsSinceEpoch()

        if start_ts >= end_ts:
            self._error_label.setText("Start time must be before end time")
            self._error_label.setVisible(True)
            return False

        self._error_label.setVisible(False)
        return True

    def _on_accept(self) -> None:
        """Handle accept button click."""
        if self._validate():
            self.accept()

    def get_range(self) -> tuple[float, float]:
        """Get the selected time range as Unix timestamps.

        Returns:
            Tuple of (start_timestamp, end_timestamp)
        """
        start_ts = float(self._start_edit.dateTime().toSecsSinceEpoch())
        end_ts = float(self._end_edit.dateTime().toSecsSinceEpoch())
        return start_ts, end_ts
