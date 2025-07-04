import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt


# 🔒 Whitelisted paths
ALLOWED_EXECUTABLE = os.path.normcase(os.path.abspath(r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\EXE\PPMv5.exe"))
ALLOWED_SCRIPT = os.path.normcase(os.path.abspath(r"C:\TrustedTools\myscript.py"))


class SecureRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Executable Runner")
        self.setMinimumSize(400, 200)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.exe_btn = QPushButton("Run Allowed EXE")
        self.py_btn = QPushButton("Run Allowed Python Script")
        self.custom_btn = QPushButton("Browse and Run (Blocked if Not Allowed)")

        self.exe_btn.clicked.connect(self.run_allowed_exe)
        self.py_btn.clicked.connect(self.run_allowed_py)
        self.custom_btn.clicked.connect(self.run_browsed_file)

        layout.addWidget(self.exe_btn)
        layout.addWidget(self.py_btn)
        layout.addWidget(self.custom_btn)

        self.setCentralWidget(central_widget)

    def run_allowed_exe(self):
        self.run_file(ALLOWED_EXECUTABLE)

    def run_allowed_py(self):
        self.run_python_script(ALLOWED_SCRIPT)

    def run_browsed_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Executable or Python Script")
        if not file_path:
            return

        norm_path = os.path.normcase(os.path.abspath(file_path))

        if norm_path == ALLOWED_EXECUTABLE:
            self.run_file(norm_path)
        elif norm_path == ALLOWED_SCRIPT:
            self.run_python_script(norm_path)
        else:
            QMessageBox.critical(self, "Access Denied", "This file is not authorized to run.")

    def run_file(self, path):
        try:
            subprocess.Popen(
                [path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            QMessageBox.information(self, "Success", f"Launched: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run file:\n{e}")

    def run_python_script(self, script_path):
        try:
            subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            QMessageBox.information(self, "Success", f"Launched script: {script_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run script:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecureRunner()
    window.show()
    sys.exit(app.exec())
