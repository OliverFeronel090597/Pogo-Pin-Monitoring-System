from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel
import os

from libs.StyleUtils import apply_stylesheet

class RccAuto(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rcc Auto")
        apply_stylesheet()

        self.label = QLabel(os.getcwd())
        self.button = QPushButton("Choose Folder")
        self.button.clicked.connect(self.select_folder)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.label.setText(f"Selected: {folder_path}")
            print("Folder path:", folder_path)

if __name__ == "__main__":
    app = QApplication([])
    win = RccAuto()
    win.show()
    app.exec()
