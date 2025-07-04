import sys
import subprocess
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restartable App")

        restart_button = QPushButton("🔄 Restart App")
        restart_button.clicked.connect(self.restart_app)

        layout = QVBoxLayout()
        layout.addWidget(restart_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def restart_app(self):
        QApplication.quit()

        # Fix for PyInstaller second restart issue
        if getattr(sys, 'frozen', False):
            executable = sys.executable
            script = os.path.abspath(sys.argv[0])
            subprocess.Popen([executable], cwd=os.getcwd())  # don't pass sys.argv again
        else:
            subprocess.Popen([sys.executable] + sys.argv)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
