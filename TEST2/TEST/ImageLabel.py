import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize


class ImageWidget(QWidget):
    def __init__(self, image_path="", parent=None):
        super().__init__(parent)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(False)

        self._original_pixmap = QPixmap(image_path)
        self._scaled_pixmap = self._original_pixmap

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.update_pixmap()

        # Allow shrinking below pixmap size
        self.label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update_pixmap(self):
        if not self._original_pixmap.isNull():
            size = self.size()
            # To avoid zero size issue:
            if size.width() > 0 and size.height() > 0:
                self._scaled_pixmap = self._original_pixmap.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.label.setPixmap(self._scaled_pixmap)

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)

    def minimumSizeHint(self):
        # Allow very small minimum size hint
        return QSize(10, 10)


class StackedWidgetContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        img_path = r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\image.png"
        self.page1 = ImageWidget(img_path)
        self.page2 = ImageWidget(img_path)
        self.page3 = ImageWidget(img_path)

        self.layout.addWidget(self.page1)
        self.layout.addWidget(self.page2)
        self.layout.addWidget(self.page3)

        self.show_page(0)

    def show_page(self, index):
        pages = [self.page1, self.page2, self.page3]
        for i, page in enumerate(pages):
            page.setVisible(i == index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MainWindow with Stackable Images")
        self.resize(300, 50)  # Start size 300x50, resizable freely

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.central_layout = QVBoxLayout()
        self.central.setLayout(self.central_layout)

        self.stacked_container = StackedWidgetContainer()
        self.central_layout.addWidget(self.stacked_container)

        btn_layout = QHBoxLayout()
        self.central_layout.addLayout(btn_layout)

        btn1 = QPushButton("Show Image 1")
        btn2 = QPushButton("Show Image 2")
        btn3 = QPushButton("Show Image 3")

        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)
        btn_layout.addWidget(btn3)

        btn1.clicked.connect(lambda: self.stacked_container.show_page(0))
        btn2.clicked.connect(lambda: self.stacked_container.show_page(1))
        btn3.clicked.connect(lambda: self.stacked_container.show_page(2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
