import sys

from PyQt6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
                             QRadioButton, QVBoxLayout, QWidget)


class RadioExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Button Example")

        layout = QVBoxLayout(self)

        # GroupBox for radio buttons
        group_box = QGroupBox("Choose an option")
        radio_layout = QVBoxLayout()

        self.radio1 = QRadioButton("Option 1")
        self.radio2 = QRadioButton("Option 2")
        self.radio3 = QRadioButton("Option 3")

        self.radio1.setChecked(True)  # default selection

        radio_layout.addWidget(self.radio1)
        radio_layout.addWidget(self.radio2)
        radio_layout.addWidget(self.radio3)
        group_box.setLayout(radio_layout)

        self.label = QLabel("Selected: Option 1")

        # Connect signals
        self.radio1.toggled.connect(self.update_selection)
        self.radio2.toggled.connect(self.update_selection)
        self.radio3.toggled.connect(self.update_selection)

        layout.addWidget(group_box)
        layout.addWidget(self.label)

    def update_selection(self):
        if self.radio1.isChecked():
            self.label.setText("Selected: Option 1")
        elif self.radio2.isChecked():
            self.label.setText("Selected: Option 2")
        elif self.radio3.isChecked():
            self.label.setText("Selected: Option 3")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RadioExample()
    window.show()
    sys.exit(app.exec())
