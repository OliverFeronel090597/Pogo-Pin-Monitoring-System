from PyQt6.QtWidgets import (
    QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QCalendarWidget, QFrame
)
from PyQt6.QtCore import QDate, Qt, QEvent, QPoint, QTimer, pyqtSignal


class DateRangePopup(QFrame):
    hidden_signal = pyqtSignal()  # Signal emitted when popup is hidden

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        today = QDate.currentDate()

        self.start_calendar = QCalendarWidget()
        self.start_calendar.setMaximumDate(today.addDays(-1))
        self.start_calendar.setSelectedDate(today.addDays(-1))

        self.end_calendar = QCalendarWidget()
        self.end_calendar.setMaximumDate(today)
        self.end_calendar.setSelectedDate(today)

        # Labels
        start_label = QLabel("Startdatum")
        end_label = QLabel("Enddatum")

        line = QFrame()
        line.setFrameShape(QFrame.Shape.WinPanel)
        line.setProperty("role", "UnderlineSeperator")

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
        self.hidden_signal.emit()
        return super().hideEvent(event)


class DateRangeLineEdit(QLineEdit):
    def __init__(self, width=200, func=None, date_now=False , parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedWidth(width)

        self.parent = parent

        self.popup = DateRangePopup(self)
        self.popup.hide()
        self.popup.hidden_signal.connect(func)

        self.popup.start_calendar.selectionChanged.connect(self.update_date_range)
        self.popup.end_calendar.selectionChanged.connect(self.update_date_range)
        if date_now:
            self.update_date_range()
        

    def mousePressEvent(self, a0):
        self.show_popup()
        return super().mousePressEvent(a0)

    def show_popup(self):
        popup_height = self.popup.sizeHint().height()
        popup_pos = self.mapToGlobal(QPoint(0, -popup_height))
        self.popup.move(popup_pos)
        self.popup.show()

    def update_date_range(self):
        start = self.popup.start_calendar.selectedDate()
        end = self.popup.end_calendar.selectedDate()
        self.setText(f"{start.toString('yyyy-MM-dd')} - {end.toString('yyyy-MM-dd')}")

    def on_popup_hidden(self):
        if self.text():
            self.parent.load_by_date()

    def focusOutEvent(self, a0):
        print("load data (focus out)")
        return super().focusOutEvent(a0)
