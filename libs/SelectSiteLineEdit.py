from PyQt6.QtWidgets import QLineEdit, QDialog
from libs.NumberInputDialog import NumberInputDialog

class SelectSite(QLineEdit):
    def __init__(self,width = 200, initial_text="Double click", parent=None):
        """Initialize the CustomLineEdit with default text."""
        super().__init__(parent)
        self.setPlaceholderText(initial_text)
        self.setMaximumWidth(width)
        self.setProperty("role", "siteInput")

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events to open a number input dialog."""
        dialog = NumberInputDialog(self.text(), self)  # Pass existing text to the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_values = dialog.selected_numbers
            sites = len(selected_values)

            if sites == 36:
                self.setText("36 sites")
            elif sites == 16:
                self.setText("16 sites")
            elif sites > 0:
                self.setText(", ".join(map(str, selected_values)))
            else:
                self.clear()

    def reset_input(self):
        """Reset the line edit text to its initial value."""
        self.clear()
