from PyQt6.QtWidgets import QSpinBox

class CustomSpinBox(QSpinBox):
    def __init__(self, width, value=0, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(width)
        self.setRange(0, 9_999_999)
        self.setSingleStep(1)
        self.setValue(value)
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)