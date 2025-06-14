from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QMenu, QToolButton
)
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QMouseEvent

import sys


class CustomHeader(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self._old_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        self.title = QLabel("Pogo Pin Monitoring")
        self.title.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.title)
        layout.addStretch()

        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: red; 
                color: white; 
                border: none;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        close_btn.clicked.connect(self.parent.close)
        layout.addWidget(close_btn)


    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._old_pos:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.parent.move(self.parent.pos() + delta)
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._old_pos = None


class CustomMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(35)
        self.setStyleSheet("background-color: #34495e;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(20)

        # Create ToolButtons with dropdown menus
        layout.addWidget(self.createMenuButton("File", ["New", "Open", "Save", "Exit"]))
        layout.addWidget(self.createMenuButton("Edit", ["Undo", "Redo", "Cut", "Copy", "Paste"]))
        layout.addWidget(self.createMenuButton("View", ["Zoom In", "Zoom Out", "Reset View"]))
        layout.addWidget(self.createMenuButton("Help", ["About", "Check for Updates"]))

        layout.addStretch()

    def createMenuButton(self, label, actions):
        button = QToolButton()
        button.setText(label)
        button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
                padding: 5px;
            }
            QToolButton::menu-indicator {
                image: none;
            }
            QToolButton:hover {
                color: #1abc9c;
            }
        """)
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(button)
        for action_text in actions:
            action = menu.addAction(action_text)
            if action_text == "Exit":
                action.triggered.connect(self.window().close)
        button.setMenu(menu)

        return button


class CustomWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.header = CustomHeader(self)
        layout.addWidget(self.header)

        self.menu = CustomMenu(self)
        layout.addWidget(self.menu)

        content = QLabel("Main Content - can't drag here")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec())
