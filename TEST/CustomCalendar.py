from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QCalendarWidget, QDialog
)
from PyQt6.QtCore import QDate, Qt
import sys


class SmartCalendar(QCalendarWidget):
    def __init__(self):
        super().__init__()

    def set_min_date_by_keyword(self, keyword):
        if keyword and keyword.lower() != "none":
            self.setMinimumDate(self._resolve_keyword(keyword))

    def set_max_date_by_keyword(self, keyword):
        if keyword and keyword.lower() != "none":
            self.setMaximumDate(self._resolve_keyword(keyword))

    def _resolve_keyword(self, keyword):
        today = QDate.currentDate()
        keyword = keyword.lower()

        match keyword:
            case "today":
                return today
            case "yesterday":
                return today.addDays(-1)
            case "tomorrow":
                return today.addDays(1)
            case "next week":
                return today.addDays(7)
            case "last week":
                return today.addDays(-7)
            case "next month":
                return today.addMonths(1)
            case "last month":
                return today.addMonths(-1)
            case _:
                return today  # fallback to today if unknown



class CalendarPopup(QDialog):
    def __init__(self, lineedit, min_keyword="yesterday", max_keyword="tomorrow"):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedSize(300, 250)

        self.lineedit = lineedit
        self.calendar = SmartCalendar()
        self.calendar.set_min_date_by_keyword(min_keyword)
        self.calendar.set_max_date_by_keyword(max_keyword)
        self.calendar.clicked.connect(self.select_date)

        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)

    def select_date(self, date):
        self.lineedit.setText(date.toString("yyyy-MM-dd"))
        self.accept()


class CalendarLineEdit(QLineEdit):
    def __init__(self, min_date_keyword="yesterday", max_date_keyword="tomorrow"):
        super().__init__()
        self.min_kw = min_date_keyword
        self.max_kw = max_date_keyword

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        popup = CalendarPopup(self, self.min_kw, self.max_kw)
        popup.move(self.mapToGlobal(self.rect().bottomLeft()))
        popup.exec()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Calendar LineEdit")
        layout = QVBoxLayout(self)

        self.date_input = CalendarLineEdit(min_date_keyword=None, max_date_keyword="today")
        layout.addWidget(self.date_input)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
