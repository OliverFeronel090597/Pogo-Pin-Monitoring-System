from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLineEdit, QLabel,
    QVBoxLayout, QHBoxLayout, QCalendarWidget, QFrame
)
from PyQt6.QtCore import QDate, Qt, QEvent, QPoint, QTimer
import sys


class DateRangePopup(QFrame):
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

        start_layout = QVBoxLayout()
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_calendar)

        end_layout = QVBoxLayout()
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_calendar)

        layout = QHBoxLayout()
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)

        self.setLayout(layout)


class DateRangeLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Hover to choose date range")
        self.setMouseTracking(True)
        self.installEventFilter(self)

        self.popup = DateRangePopup(self)
        self.popup.hide()

        self.popup.start_calendar.selectionChanged.connect(self.update_date_range)
        self.popup.end_calendar.selectionChanged.connect(self.update_date_range)

    def eventFilter(self, source, event):
        if source == self:
            if event.type() == QEvent.Type.Enter:
                self.show_popup()
            elif event.type() == QEvent.Type.Leave:
                QTimer.singleShot(300, self.hide_if_not_hovered)
        return super().eventFilter(source, event)

    def show_popup(self):
        popup_pos = self.mapToGlobal(QPoint(0, self.height()))
        self.popup.move(popup_pos)
        self.popup.show()

    def hide_if_not_hovered(self):
        if not self.popup.underMouse():
            self.popup.hide()

    def update_date_range(self):
        start = self.popup.start_calendar.selectedDate()
        end = self.popup.end_calendar.selectedDate()
        self.setText(f"{start.toString('yyyy-MM-dd')} - {end.toString('yyyy-MM-dd')}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom QLineEdit with Calendar Hover")
        self.setFixedSize(500, 300)

        self.date_line_edit = DateRangeLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.date_line_edit)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
