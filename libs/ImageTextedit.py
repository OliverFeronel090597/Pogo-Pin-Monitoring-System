from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QPainter, QPixmap
try:
    from libs.Resources import *
except ImportError:
    from Resources import *

class ImageTextedit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_pixmap = QPixmap(":/icon/logo.jpg")  # or use an absolute path
        self.setStyleSheet("background: transparent")  # Ensures QTextEdit background doesn't override

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setOpacity(0.1)  # Set opacity (0.0 - fully transparent, 1.0 - fully opaque)
        painter.drawPixmap(self.rect(), self.bg_pixmap)
        painter.setOpacity(1.0)  # Reset opacity for the text rendering
        super().paintEvent(event)
