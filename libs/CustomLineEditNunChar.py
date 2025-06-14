from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt


class NumCharLineEdit(QLineEdit):
    def __init__(self, allow_numbers_only=False, width=20, enable=True, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(width)
        self.setEnabled(enable)
        self.setProperty("role", "numCharInput")
        self.allow_numbers_only = allow_numbers_only
        self._apply_validator()

    def set_allow_numbers_only(self, state: bool):
        self.allow_numbers_only = state
        self._apply_validator()

    def _apply_validator(self):
        if self.allow_numbers_only:
            self.setValidator(QIntValidator())  # Accept only integers
        else:
            self.setValidator(None)  # Accept any characters
