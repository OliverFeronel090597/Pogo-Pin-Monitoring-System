from PyQt6.QtWidgets import (
    QVBoxLayout, QLineEdit, QCalendarWidget, QDialog
)
from PyQt6.QtCore import QDate, Qt
import sys


class SmartCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("role", "selectCalendar")

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
    def __init__(self, parent_lineedit, min_keyword="yesterday", max_keyword="tomorrow"):
        super().__init__(parent_lineedit)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedSize(300, 250)

        self.lineedit = parent_lineedit
        self.calendar = SmartCalendar(self)
        self.calendar.set_min_date_by_keyword(min_keyword)
        self.calendar.set_max_date_by_keyword(max_keyword)
        self.calendar.clicked.connect(self.select_date)

        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)

    def select_date(self, date):
        self.lineedit.setText(date.toString("yyyy-MM-dd"))
        self.accept()


class CalendarLineEdit(QLineEdit):
    """
    CalendarLineEdit is a custom QLineEdit that shows a calendar popup when clicked.

    - Displays a default date (e.g., "today") as text.
    - Allows setting a minimum and maximum date using keywords (e.g., "yesterday", "tomorrow").
    - On click, opens a CalendarPopup to select a date within the allowed range.
    """

    def __init__(self, width=200, min_date_keyword="yesterday", max_date_keyword="tomorrow", default_date="today", parent=None):
        super().__init__(parent)
        self.setMaximumWidth(width)
        self.setProperty("role", "calendarEdit")
        self.min_kw = min_date_keyword
        self.max_kw = max_date_keyword

        # Use SmartCalendar's keyword resolver to set default text
        calendar = SmartCalendar()
        default_qdate = calendar._resolve_keyword(default_date)
        self.setText(default_qdate.toString("yyyy-MM-dd"))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        popup = CalendarPopup(self, self.min_kw, self.max_kw)
        popup.move(self.mapToGlobal(self.rect().bottomLeft()))
        popup.exec()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = QWidget()
#     layout = QVBoxLayout(w)

#     cal_line_edit = CalendarLineEdit(default_date="today")
#     layout.addWidget(cal_line_edit)

#     w.show()
#     sys.exit(app.exec())
