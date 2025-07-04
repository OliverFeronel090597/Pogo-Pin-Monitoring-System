import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


# --- Regex for detecting hardcoded paths ---
win_path = re.compile(r'["\']([A-Z]:\\[^"\']+)["\']')
unix_path = re.compile(r'["\'](/[^"\']+)["\']')

def find_paths_in_file(file_path):
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, start=1):
                if win_path.search(line) or unix_path.search(line):
                    results.append((i, line.strip()))
    except Exception as e:
        results.append((0, f"[Error reading file: {e}]"))
    return results

class PathScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Local Path Scanner")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        self.info_label = QLabel("Choose your main Python script:")
        layout.addWidget(self.info_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Courier New", 10))
        layout.addWidget(self.output)

        self.btn_select = QPushButton("Select Main .py File")
        self.btn_select.clicked.connect(self.select_main_file)
        layout.addWidget(self.btn_select)

    def select_main_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Main Python File", "", "Python Files (*.py)")

        if path:
            self.output.clear()
            self.output.append(f"<b style='color:green;'>Scanning main script:</b> {path}")
            self.scan_file(path)

            libs_path = os.path.join(os.path.dirname(path), "libs")
            self.output.append(f"<br><b style='color:green;'>Scanning libs folder:</b> {libs_path}")
            self.scan_libs_folder(libs_path)

    def scan_file(self, file_path):
        matches = find_paths_in_file(file_path)
        if matches:
            self.output.append(f"<br><b style='color:red;'>[!] Found in: {file_path}</b>")
            for lineno, line in matches:
                safe_line = line.replace("<", "&lt;").replace(">", "&gt;")
                self.output.append(f"<span style='color:orange;'>Line {lineno}:</span> <span style='color:blue;'>{safe_line}</span>")
        else:
            self.output.append(f"<span style='color:gray;'>No issues found in: {file_path}</span>")

    def scan_libs_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            self.output.append(f"<span style='color:red;'>[!] 'libs' folder not found.</span>")
            return

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    self.scan_file(full_path)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PathScanner()
    window.show()
    sys.exit(app.exec())
