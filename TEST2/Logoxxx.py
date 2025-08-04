from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class StartupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Startup Logo Overlap Test")
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: white;")

        # Main label
        text_label = QLabel("Loading PPM Tool...", self)
        text_label.move(50, 200)
        text_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")

        # Floating logo label (same parent)
        self.logo_label = QLabel(self)

        # Load image
        image_path = r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\icon\image.png"
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print("⚠️ Image failed to load. Check the path:")
            print(image_path)
        else:
            # Scale and set image
            pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setStyleSheet("background: transparent;")
            self.logo_label.move(600, -50)  # Overlap top-right corner

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = StartupWindow()
    window.show()
    sys.exit(app.exec())
