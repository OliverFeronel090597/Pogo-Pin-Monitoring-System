import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QStyle
)
from PyQt6.QtCore import Qt, QPoint


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2c3e50;")

        # Title
        self.title = QLabel("Custom Frameless Window")
        self.title.setStyleSheet("color: white; font-weight: bold;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        self.btn_minimize = QPushButton()
        self.btn_maximize = QPushButton()
        self.btn_close = QPushButton()

        for btn in [self.btn_minimize, self.btn_maximize, self.btn_close]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("QPushButton { border: none; } QPushButton:hover { background-color: #34495e; }")

        # Set Qt icons
        style = QApplication.style()
        self.btn_minimize.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        self.btn_maximize.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.btn_close.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))

        # Connect signals
        self.btn_minimize.clicked.connect(self.parent.showMinimized)
        self.btn_maximize.clicked.connect(self.toggle_max_restore)
        self.btn_close.clicked.connect(self.parent.close)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)

        self.setLayout(layout)

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()


class CustomMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(800, 500)

        # Track dragging
        self._mouse_pos = None

        # Custom Title Bar
        self.title_bar = CustomTitleBar(self)

        # Main Content
        self.content = QLabel("Main Content Area")
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.setStyleSheet("font-size: 24px;")

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.content)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._mouse_pos is not None:
            self.move(event.globalPosition().toPoint() - self._mouse_pos)

    def mouseReleaseEvent(self, event):
        self._mouse_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomMainWindow()
    window.show()
    sys.exit(app.exec())
