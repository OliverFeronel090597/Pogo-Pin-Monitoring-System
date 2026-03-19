import os
import re
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QProgressBar,
    QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt, QThread, pyqtSignal


# --- Regex for detecting hardcoded paths ---
win_path = re.compile(r'["\']([A-Z]:\\[^"\']+)["\']')
unix_path = re.compile(r'["\'](/[^"\']+)["\']')
network_path = re.compile(r'["\'](\\\\[^"\']+)["\']')  # Windows network paths

class ScanWorker(QThread):
    """Worker thread for scanning files without freezing the UI"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    result = pyqtSignal(str, int, str)  # file_path, line_no, line_content
    scan_complete = pyqtSignal(int)  # total issues found
    error = pyqtSignal(str)
    
    def __init__(self, main_file, scan_libs=True):
        super().__init__()
        self.main_file = main_file
        self.scan_libs = scan_libs
        self.is_running = True
        
    def run(self):
        total_issues = 0
        files_scanned = 0
        
        # Scan main file
        self.status.emit(f"Scanning main script: {os.path.basename(self.main_file)}")
        issues = self.scan_file(self.main_file)
        total_issues += issues
        files_scanned += 1
        
        # Scan libs folder if requested
        if self.scan_libs:
            libs_path = os.path.join(os.path.dirname(self.main_file), "libs")
            if os.path.isdir(libs_path):
                self.status.emit(f"Scanning libs folder: {libs_path}")
                py_files = []
                for root, _, files in os.walk(libs_path):
                    for file in files:
                        if file.endswith(".py") and self.is_running:
                            py_files.append(os.path.join(root, file))
                
                for i, file_path in enumerate(py_files):
                    if not self.is_running:
                        break
                    self.status.emit(f"Scanning: {os.path.basename(file_path)}")
                    issues = self.scan_file(file_path)
                    total_issues += issues
                    files_scanned += 1
                    progress = int((i + 1) / len(py_files) * 100)
                    self.progress.emit(progress)
            else:
                self.error.emit("'libs' folder not found")
        
        self.scan_complete.emit(total_issues)
    
    def scan_file(self, file_path):
        issues_found = 0
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, start=1):
                    if not self.is_running:
                        break
                    if win_path.search(line) or unix_path.search(line) or network_path.search(line):
                        self.result.emit(file_path, i, line.strip())
                        issues_found += 1
        except Exception as e:
            self.error.emit(f"Error reading {os.path.basename(file_path)}: {str(e)}")
        
        return issues_found
    
    def stop(self):
        self.is_running = False

class PathScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Local Path Scanner")
        self.resize(900, 700)
        
        # Set window icon (if you have one)
        # self.setWindowIcon(QIcon("icon.png"))
        
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_label = QLabel("🔍 Python Local Path Scanner")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Instructions
        self.info_label = QLabel("Select your main Python script to scan for hardcoded paths:")
        self.info_label.setStyleSheet("color: #34495e; font-size: 12px;")
        layout.addWidget(self.info_label)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        self.btn_select = QPushButton("📂 Select Main .py File")
        self.btn_select.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_select.clicked.connect(self.select_main_file)
        control_layout.addWidget(self.btn_select)
        
        self.btn_stop = QPushButton("⏹️ Stop Scanning")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_scanning)
        self.btn_stop.setEnabled(False)
        control_layout.addWidget(self.btn_stop)
        
        self.btn_clear = QPushButton("🗑️ Clear Output")
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.btn_clear.clicked.connect(self.clear_output)
        control_layout.addWidget(self.btn_clear)
        
        layout.addLayout(control_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.libs_checkbox = QCheckBox("Scan 'libs' folder")
        self.libs_checkbox.setChecked(True)
        self.libs_checkbox.setStyleSheet("color: #34495e;")
        options_layout.addWidget(self.libs_checkbox)
        
        options_layout.addStretch()
        
        self.stats_label = QLabel("Ready to scan")
        self.stats_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        options_layout.addWidget(self.stats_label)
        
        layout.addLayout(options_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Output text area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setStyleSheet("""
            QTextEdit {
                border: 2px solid #c0c0c0;
                border-radius: 6px;
                padding: 8px;
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
            
            QTextEdit:focus {
                border-color: #3498db;
            }
            
            QTextEdit:hover {
                border-color: #95a5a6;
            }
            
            /* Scrollbar styling */
            QTextEdit QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            
            QTextEdit QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            
            QTextEdit QScrollBar::add-line:vertical, 
            QTextEdit QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            QTextEdit QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 12px;
                border-radius: 6px;
            }
            
            QTextEdit QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QTextEdit QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
        """)
        layout.addWidget(self.output)
        
        # Status bar
        self.status_label = QLabel("👆 Select a Python file to begin scanning")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def select_main_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Main Python File", "", "Python Files (*.py)")

        if path:
            self.start_scanning(path)
    
    def start_scanning(self, path):
        # Clear previous output
        self.output.clear()
        
        # Update UI state
        self.btn_select.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Display header
        self.append_html(f"<h3 style='color:#27ae60;'>📁 Scanning Started</h3>")
        self.append_html(f"<b>Main script:</b> {path}")
        
        # Create and start worker thread
        self.worker = ScanWorker(path, self.libs_checkbox.isChecked())
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.result.connect(self.add_result)
        self.worker.scan_complete.connect(self.scan_finished)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
        self.status_label.setText("Scanning in progress...")
    
    def stop_scanning(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.append_html("<br><b style='color:#e74c3c;'>⏹️ Scanning stopped by user</b>")
            self.scan_finished(-1)
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def add_result(self, file_path, line_no, line_content):
        # Format the result with colors
        relative_path = os.path.basename(file_path)
        safe_line = line_content.replace("<", "&lt;").replace(">", "&gt;")
        
        # Highlight the path in the line
        for pattern in [win_path, unix_path, network_path]:
            match = pattern.search(line_content)
            if match:
                path = match.group(1)
                highlighted_line = safe_line.replace(path, f"<span style='background-color:#ffcccc;'>{path}</span>")
                break
        else:
            highlighted_line = safe_line
        
        self.append_html(
            f"<div style='margin: 5px 0; padding: 5px; border-left: 3px solid #e74c3c; background-color: #fff9f9;'>"
            f"<b style='color:#c0392b;'>📄 {relative_path}</b><br>"
            f"<span style='color:#e67e22;'>Line {line_no}:</span> "
            f"<code style='background-color:#f0f0f0; padding: 2px;'>{highlighted_line}</code>"
            f"</div>"
        )
        
        # Auto-scroll to bottom
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output.setTextCursor(cursor)
    
    def scan_finished(self, total_issues):
        self.btn_select.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if total_issues >= 0:
            if total_issues == 0:
                summary = "<h3 style='color:#27ae60;'>✅ Scan Complete - No hardcoded paths found!</h3>"
                self.status_label.setText("Scan complete - No issues found")
            else:
                summary = f"<h3 style='color:#e74c3c;'>⚠️ Scan Complete - Found {total_issues} hardcoded path(s)</h3>"
                self.status_label.setText(f"Scan complete - Found {total_issues} issues")
            
            self.append_html(f"<br>{summary}")
        
        self.worker = None
    
    def show_error(self, error_message):
        self.append_html(f"<br><span style='color:#e74c3c;'>❌ Error: {error_message}</span>")
        QMessageBox.warning(self, "Scanning Error", error_message)
    
    def clear_output(self):
        self.output.clear()
        self.status_label.setText("Output cleared")
        self.stats_label.setText("Ready to scan")
    
    def append_html(self, html):
        self.output.append(html)
        
        # Update stats
        if "Found" in html and "path" in html:
            # Extract number from summary
            match = re.search(r'Found (\d+)', html)
            if match:
                self.stats_label.setText(f"Total issues: {match.group(1)}")

def main():
    import sys
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = PathScanner()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()