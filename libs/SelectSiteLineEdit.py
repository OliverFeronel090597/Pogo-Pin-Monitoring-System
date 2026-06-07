from PyQt6.QtWidgets import QDialog, QLineEdit

from libs.NumberInputDialog import SiteSelectDialog


class SelectSite(QLineEdit):
    def __init__(self,width = 200, initial_text="Double click", parent=None):
        """Initialize the CustomLineEdit with default text."""
        super().__init__(parent)
        self.setPlaceholderText(initial_text)
        self.setMaximumWidth(width)
        self.setProperty("role", "siteInput")

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events to open a number input dialog."""
        dialog = SiteSelectDialog(initial_sites=self.text(), parent=self)  # Pass existing text to the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_values = dialog.selected_numbers
            sites = len(selected_values)

            if sites == 36:
                self.setText("36 sites")
            elif sites == 16:
                self.setText("16 sites")
            elif sites > 0:
                self.setText(self.format_range_if_consecutive(selected_values))
            else:
                self.clear()

    def format_range_if_consecutive(self, numbers):
        """
        Returns "first..last" if numbers are consecutive with no gaps,
        otherwise returns the original list as comma-separated string.
        """
        if not numbers:
            return ""
        
        sorted_nums = sorted(set(numbers))
        first, last = sorted_nums[0], sorted_nums[-1]
        
        if len(sorted_nums) == last - first + 1:
            return f"{first}..{last}"
        else:
            return ", ".join(str(n) for n in sorted_nums)

    def reset_input(self):
        """Reset the line edit text to its initial value."""
        self.clear()
