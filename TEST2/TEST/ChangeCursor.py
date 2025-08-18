import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Cursor Example")
        layout = QVBoxLayout()
        
        self.button = QPushButton("Start Long Task")
        self.button.clicked.connect(self.start_task)
        
        layout.addWidget(self.button)
        self.setLayout(layout)

    def start_task(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QTimer.singleShot(2000, self.finish_task)  # simulate long task (2 sec)

    def finish_task(self):
        QApplication.restoreOverrideCursor()

app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
