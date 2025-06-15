from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt

from libs.CalendarLineEdit import DateRangeLineEdit


class DataGraphing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(control_layout)

        self.data_range_label = QLabel("Timeframe :")
        self.data_range_label.setMaximumWidth(self.label_width(self.data_range_label.text()))
        self.data_range = DateRangeLineEdit(width=200, func=self.funx, parent=self)

        control_layout.addWidget(self.data_range_label)
        control_layout.addWidget(self.data_range)

    def funx(self):
        pass
    

    def label_width(self, text):
        return len(text) * 10