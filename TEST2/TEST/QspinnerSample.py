from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpinBox, QLabel
from PyQt6.QtCore import Qt
import sys

class CustomSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setSingleStep(5)
        self.setValue(10)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self._style())

    def _style(self):
        return """
        QSpinBox {
            border: 2px solid #4CAF50;
            border-radius: 6px;
            padding: 4px 8px;
            background-color: #f0f0f0;
            selection-background-color: #4CAF50;
            font-size: 16px;
        }

        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #4CAF50;
            background-color: #e8f5e9;
        }

        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #4CAF50;
            background-color: #ffebee;
        }

        QSpinBox::up-arrow {
            image: url(:/qt-project.org/styles/commonstyle/images/up-16.png);
        }

        QSpinBox::down-arrow {
            image: url(:/qt-project.org/styles/commonstyle/images/down-16.png);
        }
        """


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom SpinBox")
        self.setFixedSize(250, 120)

        layout = QVBoxLayout(self)

        self.label = QLabel("Value: 10")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinbox = CustomSpinBox()
        self.spinbox.valueChanged.connect(self.update_label)

        layout.addWidget(self.spinbox)
        layout.addWidget(self.label)

    def update_label(self, val):
        self.label.setText(f"Value: {val}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Demo()
    window.show()
    sys.exit(app.exec())
