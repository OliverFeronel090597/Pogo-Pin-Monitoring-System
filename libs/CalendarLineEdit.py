from PyQt6.QtCore import QDate, QEvent, QPoint, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QCalendarWidget, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QVBoxLayout, QToolButton)
from PyQt6.QtGui import QTextCharFormat, QColor, QBrush


class SmartCalendar(QCalendarWidget):
    """
    Custom calendar widget that:
    - Disables future dates (gray color)
    - Shows Saturdays and Sundays in red
    - Preserves selection highlighting
    - Prevents navigation to months with no selectable dates
    """
    def __init__(self, parent=None, calendar_type="start"):
        super().__init__(parent)
        self.setProperty("role", "selectCalendar")
        self.calendar_type = calendar_type  # "start" or "end"
        self.linked_calendar = None  # Reference to the other calendar
        self.min_allowed_date = None  # Minimum date constraint
        
        # Set maximum date to today (disable future dates)
        self.setMaximumDate(QDate.currentDate())
        
        # Format for weekend days (Saturday and Sunday) - Red color
        self.weekend_format = QTextCharFormat()
        self.weekend_format.setForeground(QColor(255, 0, 0))  # Red
        
        # Format for disabled future dates - Gray
        self.disabled_date_format = QTextCharFormat()
        self.disabled_date_format.setForeground(QColor(126, 126, 126))  # Gray
        self.disabled_date_format.setBackground(QColor(240, 240, 240))  # Light gray background
        
        # Store selection formats
        self.selected_format = QTextCharFormat()
        self.selected_format.setBackground(QBrush(QColor(70, 130, 180)))  # Steel blue
        self.selected_format.setForeground(QBrush(Qt.GlobalColor.white))
        
        # Connect to update formatting when the month changes
        self.currentPageChanged.connect(self.update_formatting)
        
        # Connect selection changed to update formatting
        self.selectionChanged.connect(self.update_formatting)
        
        # Initial formatting
        self.update_formatting()

    def set_linked_calendar(self, calendar):
        """Set the linked calendar for constraint checking"""
        self.linked_calendar = calendar

    def set_min_allowed_date(self, date):
        """Set the minimum allowed date for this calendar"""
        self.min_allowed_date = date
        self.update_formatting()
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Enable/disable navigation buttons based on constraints"""
        # Find navigation buttons
        for child in self.children():
            if isinstance(child, QToolButton):
                # Check if this is a navigation button (previous/next)
                if child.text() in ["<", ">"] or child.text() in ["◀", "▶"]:
                    # Get the month that would be navigated to
                    current_date = self.selectedDate()
                    if child.text() in ["<", "◀"]:
                        # Previous month button
                        target_date = current_date.addMonths(-1)
                    else:
                        # Next month button
                        target_date = current_date.addMonths(1)
                    
                    # Check if target month has any valid dates
                    if self.min_allowed_date and self.min_allowed_date.isValid():
                        # Check if the target month has any date >= min_allowed_date
                        target_month_start = QDate(target_date.year(), target_date.month(), 1)
                        target_month_end = QDate(target_date.year(), target_date.month(), target_date.daysInMonth())
                        
                        # If the entire month is before min_allowed_date, disable the button
                        if target_month_end < self.min_allowed_date:
                            child.setEnabled(False)
                        else:
                            child.setEnabled(True)
                    else:
                        child.setEnabled(True)

    def update_formatting(self):
        """
        Format all dates:
        - Saturday and Sunday in red
        - Future dates in gray (disabled)
        - Preserve selected date highlighting
        """
        today = QDate.currentDate()
        selected_date = self.selectedDate()
        
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
                
                # Check if date is before minimum allowed date
                is_before_min = False
                if self.min_allowed_date and self.min_allowed_date.isValid():
                    is_before_min = date < self.min_allowed_date
                
                # Apply formatting based on date type
                if is_future or is_before_min:
                    # Future dates or dates before minimum - gray (disabled)
                    self.setDateTextFormat(date, self.disabled_date_format)
                elif is_weekend:
                    # Past/Present weekend - red
                    self.setDateTextFormat(date, self.weekend_format)
        
        # Re-apply selection highlight if there is a selected date
        if selected_date.isValid():
            self.setDateTextFormat(selected_date, self.selected_format)
        
        # Update navigation buttons
        self.update_navigation_buttons()
        
        # Force calendar to update
        self.update()

    def mousePressEvent(self, event):
        """
        Override mouse press to prevent selecting future dates or dates before minimum.
        """
        # Get the position of the click
        pos = event.pos()
        
        # Get the date at the click position
        date = self._get_date_at_pos(pos)
        
        if date.isValid():
            # Check if date is in the future
            if date > QDate.currentDate():
                event.ignore()
                return
            
            # Check if date is before minimum allowed date
            if self.min_allowed_date and self.min_allowed_date.isValid():
                if date < self.min_allowed_date:
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
            if hasattr(self, 'cellAt'):
                cell = self.cellAt(pos)
                if cell:
                    return cell.row(), cell.column()
        except:
            pass
        
        # Fallback: calculate from position
        header_height = 20
        cell_size = 30
        
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
        current_date = self.selectedDate()
        year = current_date.year()
        month = current_date.month()
        
        return QDate(year, month, 1)


class DateRangePopup(QFrame):
    """
    Popup frame that displays two QCalendarWidgets for selecting a start and end date.
    Both calendars stay in sync - changing one updates the other.

    Attributes:
        hidden_signal (pyqtSignal): Signal emitted when the popup is hidden.
        start_calendar (SmartCalendar): Calendar for selecting the start date.
        end_calendar (SmartCalendar): Calendar for selecting the end date.
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

        # Start calendar setup - using SmartCalendar
        self.start_calendar = SmartCalendar(calendar_type="start")
        self.start_calendar.setMaximumDate(today)
        self.start_calendar.setSelectedDate(today.addDays(-30))

        # End calendar setup - using SmartCalendar
        self.end_calendar = SmartCalendar(calendar_type="end")
        self.end_calendar.setMaximumDate(today)
        self.end_calendar.setSelectedDate(today)
        
        # Link calendars together
        self.start_calendar.set_linked_calendar(self.end_calendar)
        self.end_calendar.set_linked_calendar(self.start_calendar)
        
        # Set initial minimum date for end calendar (based on start date)
        self.update_end_calendar_constraint()

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

        # Flag to prevent recursive updates
        self._updating = False

        # Connect signals
        self.start_calendar.selectionChanged.connect(self.on_start_date_changed)
        self.end_calendar.selectionChanged.connect(self.on_end_date_changed)
        
        # Connect currentPageChanged to update highlighting when scrolling
        self.start_calendar.currentPageChanged.connect(self.update_highlighting)
        self.end_calendar.currentPageChanged.connect(self.update_highlighting)

        # Initial highlighting
        self.update_highlighting()

    def update_end_calendar_constraint(self):
        """Update the end calendar's minimum date based on start date"""
        start_date = self.start_calendar.selectedDate()
        if start_date.isValid():
            # End calendar cannot select dates before start date
            self.end_calendar.set_min_allowed_date(start_date)

    def on_start_date_changed(self):
        """
        When start date changes, if start date > end date, move end date forward.
        Also update end calendar constraints.
        """
        if self._updating:
            return

        self._updating = True
        start_date = self.start_calendar.selectedDate()
        
        # Update end calendar constraint
        self.update_end_calendar_constraint()
        
        # Get current end date
        end_date = self.end_calendar.selectedDate()
        
        # If start date is after end date, move end date to match start date
        if start_date.isValid() and end_date.isValid() and start_date > end_date:
            # Move end date to start date
            new_end = start_date
            max_date = self.end_calendar.maximumDate()
            if new_end > max_date:
                new_end = max_date
            self.end_calendar.setSelectedDate(new_end)
        
        self._updating = False
        self.update_highlighting()

    def on_end_date_changed(self):
        """
        When end date changes, if end date < start date, move start date backward.
        """
        if self._updating:
            return

        self._updating = True
        end_date = self.end_calendar.selectedDate()
        
        # Get current start date
        start_date = self.start_calendar.selectedDate()
        
        # If end date is before start date, move start date backward to match end date
        if start_date.isValid() and end_date.isValid() and end_date < start_date:
            # Move start date to end date
            new_start = end_date
            min_date = self.start_calendar.minimumDate()
            if new_start < min_date:
                new_start = min_date
            self.start_calendar.setSelectedDate(new_start)
            # Update end calendar constraint after start date changes
            self.update_end_calendar_constraint()
        
        self._updating = False
        self.update_highlighting()

    def update_highlighting(self):
        """
        Highlight the selected dates on both calendars.
        Start date in dark blue, end date in orange.
        """
        start_date = self.start_calendar.selectedDate()
        end_date = self.end_calendar.selectedDate()

        # Set up highlight formats
        start_format = QTextCharFormat()
        start_format.setBackground(QBrush(QColor(70, 130, 180)))  # Steel blue
        start_format.setForeground(QBrush(Qt.GlobalColor.white))

        end_format = QTextCharFormat()
        end_format.setBackground(QBrush(QColor(255, 140, 0)))  # Orange
        end_format.setForeground(QBrush(Qt.GlobalColor.white))

        # First, let SmartCalendar apply its formatting (weekend red, disabled gray)
        self.start_calendar.update_formatting()
        self.end_calendar.update_formatting()

        # Then apply selection highlights on top
        if start_date.isValid():
            self.start_calendar.setDateTextFormat(start_date, start_format)
            self.end_calendar.setDateTextFormat(start_date, start_format)
        
        if end_date.isValid():
            self.start_calendar.setDateTextFormat(end_date, end_format)
            self.end_calendar.setDateTextFormat(end_date, end_format)

        # Also highlight the range in light blue on both calendars
        if start_date.isValid() and end_date.isValid():
            range_format = QTextCharFormat()
            range_format.setBackground(QBrush(QColor(173, 216, 230)))  # Light blue
            range_format.setForeground(QBrush(Qt.GlobalColor.black))

            # Ensure start <= end
            if start_date > end_date:
                start_date, end_date = end_date, start_date

            current = start_date.addDays(1)
            while current < end_date:
                self.start_calendar.setDateTextFormat(current, range_format)
                self.end_calendar.setDateTextFormat(current, range_format)
                current = current.addDays(1)

        # Force calendars to update
        self.start_calendar.update()
        self.end_calendar.update()

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
        self.setReadOnly(True)

        self.parent = parent

        # Popup initialization
        self.popup = DateRangePopup(self)
        self.popup.hide()
        
        # Connect popup hidden signal
        self.popup.hidden_signal.connect(self.update_text)
        if func:
            self.popup.hidden_signal.connect(func)

        # Connect calendar changes to update text
        self.popup.start_calendar.selectionChanged.connect(self.update_text)
        self.popup.end_calendar.selectionChanged.connect(self.update_text)
        
        if date_now:
            QTimer.singleShot(0, self.update_text)

    def mousePressEvent(self, a0):
        self.show_popup()
        return super().mousePressEvent(a0)

    def show_popup(self):
        popup_height = self.popup.sizeHint().height()
        popup_pos = self.mapToGlobal(QPoint(0, -popup_height))
        self.popup.move(popup_pos)
        self.popup.show()

    def update_text(self):
        start = self.popup.start_calendar.selectedDate()
        end = self.popup.end_calendar.selectedDate()
        
        if start.isValid() and end.isValid():
            self.setText(f"{start.toString('yyyy-MM-dd')} - {end.toString('yyyy-MM-dd')}")
        elif start.isValid():
            self.setText(f"{start.toString('yyyy-MM-dd')} - ?")
        elif end.isValid():
            self.setText(f"? - {end.toString('yyyy-MM-dd')}")
        else:
            self.setText("Select date range")
            
        if hasattr(self.parent, 'load_by_date'):
            try:
                self.parent.load_by_date()
            except AttributeError:
                pass

    def get_start_date(self):
        return self.popup.start_calendar.selectedDate()
    
    def get_end_date(self):
        return self.popup.end_calendar.selectedDate()
    
    def set_start_date(self, date):
        if date.isValid():
            self.popup.start_calendar.setSelectedDate(date)
        else:
            self.popup.start_calendar.setSelectedDate(QDate())
        
    def set_end_date(self, date):
        if date.isValid():
            self.popup.end_calendar.setSelectedDate(date)
        else:
            self.popup.end_calendar.setSelectedDate(QDate())
    
    def on_popup_hidden(self):
        if self.text():
            if hasattr(self.parent, 'load_by_date'):
                try:
                    self.parent.load_by_date()
                except AttributeError:
                    pass

    def focusOutEvent(self, a0):
        print("load data (focus out)")
        return super().focusOutEvent(a0)