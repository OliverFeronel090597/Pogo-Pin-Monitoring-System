import sys

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtWidgets import QApplication, QCalendarWidget, QDialog, QLineEdit, QVBoxLayout, QWidget


class SmartCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("role", "selectCalendar")
        
        # Set maximum date to today (disable future dates)
        self.setMaximumDate(QDate.currentDate())
        
        # Format for weekend days (Saturday and Sunday) - Red color
        self.weekend_format = QTextCharFormat()
        self.weekend_format.setForeground(QColor(255, 0, 0))  # Red
        
        # Format for disabled future dates - Light red
        self.disabled_date_format = QTextCharFormat()
        self.disabled_date_format.setForeground(QColor(126, 126, 126))  # Light red
        self.disabled_date_format.setBackground(QColor(255, 240, 240))  # Very light red background
        
        # Format for disabled weekend dates - Light red with red tint
        self.disabled_weekend_format = QTextCharFormat()
        self.disabled_weekend_format.setForeground(QColor(255, 150, 150))  # Light red
        self.disabled_weekend_format.setBackground(QColor(255, 230, 230))  # Light red background
        
        # Connect to update formatting when the month changes
        self.currentPageChanged.connect(self.update_formatting)
        
        # Initial formatting
        self.update_formatting()

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

    def update_formatting(self):
        """
        Format all dates:
        - Saturday and Sunday in red
        - Future dates in light red (disabled)
        - Future weekend dates in light red with red tint
        """
        today = QDate.currentDate()
        
        # Clear previous formatting
        self.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Get the current month's date range
        current_date = self.selectedDate()
        
        # Check multiple months to ensure all visible dates are formatted
        for month_offset in range(-1, 3):  # Previous month to 2 months ahead
            check_date = current_date.addMonths(month_offset)
            year = check_date.year()
            month = check_date.month()
            
            for day in range(1, check_date.daysInMonth() + 1):
                date = QDate(year, month, day)
                
                # Check if it's a weekend (Saturday or Sunday)
                day_of_week = date.dayOfWeek()
                is_weekend = (day_of_week == Qt.DayOfWeek.Saturday or 
                             day_of_week == Qt.DayOfWeek.Sunday)
                
                # Check if it's a future date
                is_future = date > today
                
                if is_future:
                    if is_weekend:
                        # Future weekend - light red with red tint
                        self.setDateTextFormat(date, self.disabled_weekend_format)
                    else:
                        # Future weekday - light red
                        self.setDateTextFormat(date, self.disabled_date_format)
                else:
                    if is_weekend:
                        # Past/Present weekend - red
                        self.setDateTextFormat(date, self.weekend_format)

    def mousePressEvent(self, event):
        """
        Override mouse press to prevent selecting future dates.
        """
        # Get the position of the click
        pos = event.pos()
        
        # Get the date at the click position
        date = self._get_date_at_pos(pos)
        
        if date.isValid() and date > QDate.currentDate():
            # If it's a future date, ignore the click
            event.ignore()
            return
        super().mousePressEvent(event)

    def _get_date_at_pos(self, pos):
        """
        Helper method to get the date at a specific position.
        """
        # Get the cell position
        cell_pos = self._get_cell_at_pos(pos)
        if cell_pos is None:
            return QDate()
        
        row, col = cell_pos
        
        # Row 0 is the header, rows 1-6 are for dates
        if row <= 0:  # Header row
            return QDate()
        
        # Get the first day of the current month view
        first_day = self._get_first_day_of_month_view()
        if not first_day.isValid():
            return QDate()
        
        # Calculate the date
        first_day_of_week = self.firstDayOfWeek()
        
        # Adjust for first day of week
        if first_day_of_week == Qt.DayOfWeek.Monday:
            offset = first_day.dayOfWeek() - 1  # Monday is 1
        else:
            offset = first_day.dayOfWeek() - 1  # Sunday is 7, Monday is 1
        
        # Calculate the date
        day_offset = ((row - 1) * 7) + col - offset
        date = first_day.addDays(day_offset)
        
        return date

    def _get_cell_at_pos(self, pos):
        """
        Get the cell (row, col) at the given position.
        """
        # Use the calendar's cellAt method (if available)
        try:
            # Try to use the internal method
            if hasattr(self, 'cellAt'):
                cell = self.cellAt(pos)
                if cell:
                    return cell.row(), cell.column()
        except:
            pass
        
        # Fallback: calculate from position
        header_height = 20  # Approximate header height
        cell_size = 30  # Approximate cell size
        
        if pos.y() < header_height:
            return None
        
        row = int((pos.y() - header_height) / cell_size) + 1
        col = int(pos.x() / cell_size)
        
        if row < 1 or row > 6 or col < 0 or col > 6:
            return None
        
        return row, col

    def _get_first_day_of_month_view(self):
        """
        Get the first day of the current month view.
        """
        # Get the current month/year from the displayed date
        current_date = self.selectedDate()
        year = current_date.year()
        month = current_date.month()
        
        return QDate(year, month, 1)


class CalendarPopup(QDialog):
    def __init__(self, parent_lineedit, min_keyword="yesterday", max_keyword="tomorrow"):
        super().__init__(parent_lineedit)
        self.setWindowFlags(Qt.WindowType.Popup)
        # self.setFixedSize(300, 250)

        self.lineedit = parent_lineedit 
        self.calendar = SmartCalendar(self)
        self.calendar.set_min_date_by_keyword(min_keyword)
        self.calendar.set_max_date_by_keyword(max_keyword)
        self.calendar.clicked.connect(self.select_date)

        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)

    def select_date(self, date):
        # Only allow selection if date is not in the future
        if date <= QDate.currentDate():
            self.lineedit.setText(date.toString("yyyy-MM-dd"))
            self.accept()


class CalendarLineEdit(QLineEdit):
    """
    CalendarLineEdit is a custom QLineEdit that shows a calendar popup when clicked.

    - Displays a default date (e.g., "today") as text.
    - Allows setting a minimum and maximum date using keywords (e.g., "yesterday", "tomorrow").
    - On click, opens a CalendarPopup to select a date within the allowed range.
    - Future dates are disabled and shown in light red.
    - Saturdays and Sundays are shown in red (future weekends in light red).
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    layout = QVBoxLayout(w)

    cal_line_edit = CalendarLineEdit(default_date="today")
    layout.addWidget(cal_line_edit)

    w.show()
    sys.exit(app.exec())