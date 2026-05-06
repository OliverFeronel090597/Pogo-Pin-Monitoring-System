import fnmatch
import os
import sys
from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class LineCounter(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    file_processed = pyqtSignal(str, int)
    
    def __init__(self):
        super().__init__()
        self.paths = []
        self.file_patterns = []
        self.running = True
        
    def run(self):
        all_files = []
        total_lines = 0
        file_stats = {}
        
        # Collect all matching files
        for path in self.paths:
            path = Path(path)
            if path.is_file():
                if self._should_include_file(path):
                    all_files.append(path)
            elif path.is_dir():
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = Path(root) / file
                        if self._should_include_file(file_path):
                            all_files.append(file_path)
        
        # Count lines in each file
        total_files = len(all_files)
        for idx, file_path in enumerate(all_files):
            if not self.running:
                break
                
            try:
                line_count = self._count_lines_in_file(file_path)
                file_stats[str(file_path)] = line_count
                total_lines += line_count
                self.file_processed.emit(str(file_path), line_count)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
            
            self.progress.emit(int((idx + 1) / total_files * 100))
        
        self.result.emit({
            'total_files': len(file_stats),
            'total_lines': total_lines,
            'file_stats': file_stats
        })
    
    def _should_include_file(self, file_path):
        if not file_path.is_file():
            return False
        for pattern in self.file_patterns:
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        return False
    
    def _count_lines_in_file(self, file_path):
        count = 0
        in_multiline_comment = False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Handle multiline comments
                    if '/*' in line and '*/' in line:
                        # Line contains both start and end of multiline comment
                        # Count only text outside comments
                        parts = line.split('/*')
                        for i, part in enumerate(parts):
                            if i == 0:
                                # Text before first /*
                                if part and not part.startswith('*'):
                                    count += 1
                            else:
                                # After /*, check for */
                                if '*/' in part:
                                    after_comment = part.split('*/', 1)[1]
                                    if after_comment.strip():
                                        count += 1
                    elif '/*' in line:
                        in_multiline_comment = True
                        parts = line.split('/*', 1)
                        if parts[0].strip() and not parts[0].strip().startswith('*'):
                            count += 1
                    elif '*/' in line:
                        in_multiline_comment = False
                        parts = line.split('*/', 1)
                        if parts[1].strip():
                            count += 1
                    elif not in_multiline_comment:
                        # Skip single line comments
                        if line.startswith('//') or line.startswith('#'):
                            continue
                        count += 1
        except (UnicodeDecodeError, PermissionError):
            pass
            
        return count
    
    def stop(self):
        self.running = False

class FilePatternDialog(QDialog):
    def __init__(self, parent=None, current_patterns=None):
        super().__init__(parent)
        self.setWindowTitle("File Patterns")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Pattern input
        input_layout = QHBoxLayout()
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("e.g., *.py, *.cpp, *.js")
        input_layout.addWidget(self.pattern_input)
        
        self.add_btn = QPushButton("Add Pattern")
        self.add_btn.clicked.connect(self.add_pattern)
        input_layout.addWidget(self.add_btn)
        
        layout.addLayout(input_layout)
        
        # Pattern list
        self.pattern_list = QListWidget()
        if current_patterns:
            self.pattern_list.addItems(current_patterns)
        layout.addWidget(self.pattern_list)
        
        # Remove button
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_pattern)
        layout.addWidget(remove_btn)
        
        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def add_pattern(self):
        pattern = self.pattern_input.text().strip()
        if pattern:
            self.pattern_list.addItem(pattern)
            self.pattern_input.clear()
    
    def remove_pattern(self):
        for item in self.pattern_list.selectedItems():
            self.pattern_list.takeItem(self.pattern_list.row(item))
    
    def get_patterns(self):
        return [self.pattern_list.item(i).text() 
                for i in range(self.pattern_list.count())]

class PathSelectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Path list
        self.path_list = QListWidget()
        self.path_list.setMaximumHeight(100)
        layout.addWidget(self.path_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_file_btn = QPushButton("Add Files")
        self.add_file_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_file_btn)
        
        self.add_dir_btn = QPushButton("Add Directory")
        self.add_dir_btn.clicked.connect(self.add_directory)
        btn_layout.addWidget(self.add_dir_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "", "All Files (*)"
        )
        for file in files:
            if file not in self.get_paths():
                self.path_list.addItem(file)
    
    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory"
        )
        if directory and directory not in self.get_paths():
            self.path_list.addItem(directory)
    
    def remove_selected(self):
        for item in self.path_list.selectedItems():
            self.path_list.takeItem(self.path_list.row(item))
    
    def clear_all(self):
        self.path_list.clear()
    
    def get_paths(self):
        return [self.path_list.item(i).text() 
                for i in range(self.path_list.count())]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.line_counter = None
        self.file_patterns = ['*.py', '*.cpp', '*.c', '*.h', '*.js', '*.html', '*.css', '*.java']
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        self.setWindowTitle("Code Line Counter")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("📊 Code Line Counter")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Path selector
        path_group = QGroupBox("Select Files/Directories")
        path_layout = QVBoxLayout(path_group)
        self.path_selector = PathSelectorWidget()
        path_layout.addWidget(self.path_selector)
        main_layout.addWidget(path_group)
        
        # File patterns
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("File Patterns:"))
        
        self.pattern_display = QLineEdit()
        self.pattern_display.setText(', '.join(self.file_patterns))
        self.pattern_display.setReadOnly(True)
        pattern_layout.addWidget(self.pattern_display)
        
        self.pattern_btn = QPushButton("Configure Patterns")
        self.pattern_btn.clicked.connect(self.configure_patterns)
        pattern_layout.addWidget(self.pattern_btn)
        
        main_layout.addLayout(pattern_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        main_layout.addWidget(self.status_label)
        
        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Lines", "Progress"])
        self.results_tree.setColumnWidth(0, 400)
        self.results_tree.setColumnWidth(1, 100)
        main_layout.addWidget(self.results_tree)
        
        # Summary section
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        self.total_files_label = QLabel("Files: 0")
        self.total_lines_label = QLabel("Total Lines: 0")
        self.avg_lines_label = QLabel("Avg/File: 0")
        
        for label in [self.total_files_label, self.total_lines_label, self.avg_lines_label]:
            label.setObjectName("summaryLabel")
            summary_layout.addWidget(label)
        
        main_layout.addWidget(summary_group)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Counting")
        self.start_btn.clicked.connect(self.start_counting)
        self.start_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_counting)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑 Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        btn_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Connect signals
        self.path_selector.path_list.itemSelectionChanged.connect(self.update_start_button)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #e0e0e0;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e0e0e0;
            }
            
            #headerLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4a9eff;
                padding: 15px;
                background-color: #1e1e1e;
                border-radius: 5px;
            }
            
            QPushButton {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 8px 15px;
                font-size: 12px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #4a9eff;
            }
            
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
                border-color: #3c3c3c;
            }
            
            QLineEdit, QListWidget, QTreeWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #4a9eff;
            }
            
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #4a9eff;
                color: white;
            }
            
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                text-align: center;
                color: white;
                background-color: #1e1e1e;
            }
            
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 2px;
            }
            
            #statusLabel {
                color: #888888;
                font-style: italic;
                padding: 5px;
            }
            
            #summaryLabel {
                font-size: 14px;
                font-weight: bold;
                color: #4a9eff;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
                margin: 2px;
            }
            
            QHeaderView::section {
                background-color: #3c3c3c;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
            }
            
            QDialog {
                background-color: #2b2b2b;
            }
            
            QDialog QLabel {
                color: #e0e0e0;
            }
        """)
    
    def configure_patterns(self):
        dialog = FilePatternDialog(self, self.file_patterns)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.file_patterns = dialog.get_patterns()
            self.pattern_display.setText(', '.join(self.file_patterns) if self.file_patterns else 'None')
    
    def update_start_button(self):
        self.start_btn.setEnabled(self.path_selector.path_list.count() > 0)
    
    def start_counting(self):
        # Clear previous results
        self.results_tree.clear()
        self.total_files_label.setText("Files: 0")
        self.total_lines_label.setText("Total Lines: 0")
        self.avg_lines_label.setText("Avg/File: 0")
        
        # Setup counter thread
        self.line_counter = LineCounter()
        self.line_counter.paths = self.path_selector.get_paths()
        self.line_counter.file_patterns = self.file_patterns
        
        # Connect signals
        self.line_counter.progress.connect(self.update_progress)
        self.line_counter.result.connect(self.show_results)
        self.line_counter.file_processed.connect(self.add_file_result)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Counting lines...")
        
        # Start counting
        self.line_counter.start()
    
    def stop_counting(self):
        if self.line_counter:
            self.line_counter.stop()
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Counting stopped")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def add_file_result(self, file_path, line_count):
        item = QTreeWidgetItem(self.results_tree)
        item.setText(0, file_path)
        item.setText(1, str(line_count))
        
        # Add progress bar in third column
        progress_bar = QProgressBar()
        progress_bar.setMaximum(line_count)
        progress_bar.setValue(line_count)
        progress_bar.setFormat("%v lines")
        self.results_tree.setItemWidget(item, 2, progress_bar)
        
        # Color code based on file size
        if line_count > 1000:
            item.setForeground(1, QBrush(QColor(255, 100, 100)))  # Red for large files
        elif line_count > 500:
            item.setForeground(1, QBrush(QColor(255, 255, 100)))  # Yellow for medium files
        else:
            item.setForeground(1, QBrush(QColor(100, 255, 100)))  # Green for small files
    
    def show_results(self, stats):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Update summary
        self.total_files_label.setText(f"Files: {stats['total_files']}")
        self.total_lines_label.setText(f"Total Lines: {stats['total_lines']}")
        avg_lines = stats['total_lines'] // stats['total_files'] if stats['total_files'] > 0 else 0
        self.avg_lines_label.setText(f"Avg/File: {avg_lines}")
        
        self.status_label.setText(f"Completed! Found {stats['total_lines']} lines in {stats['total_files']} files")
        
        # Sort by line count
        self.results_tree.sortItems(1, Qt.SortOrder.DescendingOrder)
    
    def clear_results(self):
        self.results_tree.clear()
        self.total_files_label.setText("Files: 0")
        self.total_lines_label.setText("Total Lines: 0")
        self.avg_lines_label.setText("Avg/File: 0")
        self.status_label.setText("Ready")

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()