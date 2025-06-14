from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class ImageLabel(QLabel):
    def __init__(self, image_path="", parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)  # Don't stretch automatically
        self.setStyleSheet("background: transparent;")  # Avoid redraw flickers
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self._original_pixmap = QPixmap(image_path)
        self._scaled_pixmap = self._original_pixmap
        self.setPixmap(self._scaled_pixmap)

    def update_pixmap(self):
        if not self._original_pixmap.isNull():
            size = self.size()
            if size.width() > 0 and size.height() > 0:
                self._scaled_pixmap = self._original_pixmap.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(self._scaled_pixmap)

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)
