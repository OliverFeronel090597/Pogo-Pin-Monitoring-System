from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QIcon
import sys

class IconButtonDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button with Icon and Label")
        self.setFixedSize(300, 100)

        # Layout
        layout = QVBoxLayout()

        # Create button
        button = QPushButton("Open Folder")
        button.setIcon(QIcon("folder.png"))  # Replace with your icon path
        button.setIconSize(button.sizeHint())  # Optional: adjust icon size
        layout.addWidget(button)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IconButtonDemo()
    window.show()
    sys.exit(app.exec())
