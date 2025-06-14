from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
import sys


class MessagePopup(QWidget):
    def __init__(self, title="Warning", content="Something went wrong!", icon_type="warning", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # So it doesn't show in taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                border: 2px solid #f39c12;
                border-radius: 10px;
                color: #ECF0F1;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }
            QLabel#title {
                font-size: 13pt;
                font-weight: bold;
            }
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
        """)

        self._build_ui(title, content, icon_type)

    def _build_ui(self, title, content, icon_type):
        layout = QVBoxLayout(self)

        title_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 24pt; margin-right: 10px;")
        icon_label.setFixedSize(32, 32)

        title_text = QLabel(title)
        title_text.setObjectName("title")

        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_text)
        layout.addLayout(title_layout)

        message = QLabel(content)
        message.setWordWrap(True)
        layout.addWidget(message)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.close)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)



# Test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    popup = MessagePopup(
        title="Warning",
        content="This action could not be completed. Please try again.",
        icon_type="warning"
    )
    popup.show()
    sys.exit(app.exec())
