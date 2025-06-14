from PyQt6.QtWidgets import QComboBox

class CustomDropdown(QComboBox):
    def __init__(self, items, width, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(width)
        self.setProperty('role', "sapNumber")
        self.setEditable(False)  # Make True if you want user to type
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        if items:
            self.addItems(items)