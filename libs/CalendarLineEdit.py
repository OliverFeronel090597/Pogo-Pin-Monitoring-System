from PyQt6.QtWidgets import (
    QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QCalendarWidget, QFrame
)
from PyQt6.QtCore import QDate, Qt, QEvent, QPoint, QTimer, pyqtSignal


class DateRangePopup(QFrame):
    """
    Popup frame that displays two QCalendarWidgets for selecting a start and end date.

    Attributes:
        hidden_signal (pyqtSignal): Signal emitted when the popup is hidden.
        start_calendar (QCalendarWidget): Calendar for selecting the start date.
        end_calendar (QCalendarWidget): Calendar for selecting the end date.
    """
    hidden_signal = pyqtSignal()  # Signal emitted when popup is hidden

    def __init__(self, parent=None):
        """
        Initialize the DateRangePopup.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent, Qt.WindowType.Popup)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        today = QDate.currentDate()

        # Start calendar setup
        self.start_calendar = QCalendarWidget()
        self.start_calendar.setMaximumDate(today.addDays(-1))
        self.start_calendar.setSelectedDate(today.addDays(-1))

        # End calendar setup
        self.end_calendar = QCalendarWidget()
        self.end_calendar.setMaximumDate(today)
        self.end_calendar.setSelectedDate(today)

        # Labels
        start_label = QLabel("Startdatum")
        end_label = QLabel("Enddatum")

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.WinPanel)
        line.setProperty("role", "UnderlineSeperator")

        # Layouts
        start_layout = QVBoxLayout()
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_calendar)

        end_layout = QVBoxLayout()
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_calendar)

        layout = QHBoxLayout()
        layout.addLayout(start_layout)
        layout.addWidget(line)
        layout.addLayout(end_layout)

        self.setLayout(layout)

    def hideEvent(self, event):
        """
        Override hideEvent to emit a hidden signal when the popup is hidden.

        Args:
            event (QHideEvent): The hide event.

        Returns:
            QHideEvent: The result of the superclass hideEvent.
        """
        self.hidden_signal.emit()
        return super().hideEvent(event)


class DateRangeLineEdit(QLineEdit):
    """
    QLineEdit widget that shows a DateRangePopup when clicked and displays
    the selected date range.

    Attributes:
        popup (DateRangePopup): The date range selection popup.
        parent (QWidget): Parent widget (optional, used for callbacks).
    """

    def __init__(self, width=200, func=None, date_now=False, parent=None):
        """
        Initialize the DateRangeLineEdit.

        Args:
            width (int, optional): Width of the line edit. Defaults to 200.
            func (callable, optional): Function to call when popup is hidden. Defaults to None.
            date_now (bool, optional): Whether to update the text immediately with current date. Defaults to False.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedWidth(width)

        self.parent = parent

        # Popup initialization
        self.popup = DateRangePopup(self)
        self.popup.hide()
        self.popup.hidden_signal.connect(func)

        # Connect calendar changes
        self.popup.start_calendar.selectionChanged.connect(self.update_date_range)
        self.popup.end_calendar.selectionChanged.connect(self.update_date_range)
        if date_now:
            self.update_date_range()

    def mousePressEvent(self, a0):
        """
        Override mouse press event to show the date range popup.

        Args:
            a0 (QMouseEvent): Mouse press event.

        Returns:
            QMouseEvent: The result of the superclass mousePressEvent.
        """
        self.show_popup()
        return super().mousePressEvent(a0)

    def show_popup(self):
        """
        Show the popup just above the line edit.
        """
        popup_height = self.popup.sizeHint().height()
        popup_pos = self.mapToGlobal(QPoint(0, -popup_height))
        self.popup.move(popup_pos)
        self.popup.show()

    def update_date_range(self):
        """
        Update the text of the line edit based on the selected dates
        from the start and end calendars.
        """
        start = self.popup.start_calendar.selectedDate()
        end = self.popup.end_calendar.selectedDate()
        self.setText(f"{start.toString('yyyy-MM-dd')} - {end.toString('yyyy-MM-dd')}")

    def on_popup_hidden(self):
        """
        Callback function when the popup is hidden. Calls parent's
        load_by_date method if text is set.
        """
        if self.text():
            self.parent.load_by_date()

    def focusOutEvent(self, a0):
        """
        Override focus out event to perform data loading action.

        Args:
            a0 (QFocusEvent): Focus out event.

        Returns:
            QFocusEvent: The result of the superclass focusOutEvent.
        """
        print("load data (focus out)")
        return super().focusOutEvent(a0)
