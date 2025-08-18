import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer


class SnapPreview(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 100)

        layout = QHBoxLayout(self)
        self.btn_left = QPushButton("⯇")
        self.btn_max = QPushButton("⬜")
        self.btn_right = QPushButton("⯈")

        for btn in (self.btn_left, self.btn_max, self.btn_right):
            btn.setFixedSize(60, 80)
            layout.addWidget(btn)


class SnapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setMinimumSize(500, 300)
        self._drag_pos = None
        self._snapped = False

        self.snap_menu = SnapPreview(self)
        self.snap_menu.btn_left.clicked.connect(self.snap_left)
        self.snap_menu.btn_right.clicked.connect(self.snap_right)
        self.snap_menu.btn_max.clicked.connect(self.snap_max)

        # === Custom title bar ===
        title_bar = QHBoxLayout()
        self.btn_close = QPushButton("✖")
        self.btn_maximize = QPushButton("▢")
        self.btn_minimize = QPushButton("—")
        self.btn_maximize.installEventFilter(self)

        for btn in [self.btn_minimize, self.btn_maximize, self.btn_close]:
            btn.setFixedSize(30, 25)
            title_bar.addWidget(btn)

        self.btn_close.clicked.connect(self.close)
        self.btn_minimize.clicked.connect(self.showMinimized)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(title_bar)

        label = QLabel("🪟 Custom Snap Layout with Aero Drag Enabled")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self.check_snap(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._snapped = False

    def check_snap(self, pos: QPoint):
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 20
        if not self._snapped:
            if abs(pos.x() - screen.left()) < margin:
                self.snap_left()
            elif abs(pos.x() - screen.right()) < margin:
                self.snap_right()
            elif abs(pos.y() - screen.top()) < margin:
                self.snap_max()

    def snap_left(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(QRect(screen.left(), screen.top(), screen.width() // 2, screen.height()))
        self._snapped = True

    def snap_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(QRect(screen.center().x(), screen.top(), screen.width() // 2, screen.height()))
        self._snapped = True

    def snap_max(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self._snapped = True

    def eventFilter(self, source, event):
        if source == self.btn_maximize:
            if event.type() == event.Type.Enter:
                self.show_snap_preview()
            elif event.type() == event.Type.Leave:
                QTimer.singleShot(500, self.hide_snap_preview)
        return super().eventFilter(source, event)

    def show_snap_preview(self):
        self.snap_menu.move(self.mapToGlobal(self.btn_maximize.pos()) + QPoint(-50, 30))
        self.snap_menu.show()

    def hide_snap_preview(self):
        if not self.snap_menu.underMouse():
            self.snap_menu.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SnapWindow()
    win.show()
    sys.exit(app.exec())
