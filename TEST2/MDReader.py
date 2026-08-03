import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QPushButton, QFileDialog,
    QLabel, QSplitter, QMessageBox, QLineEdit, QListWidget,
    QListWidgetItem, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QDir, QFileSystemWatcher
from PyQt6.QtGui import QFont, QAction, QIcon, QKeySequence
import markdown
from markdown.extensions import Extension
import re

class MarkdownReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
        self.watch_directory = None
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Markdown Reader")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel (file browser)
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        # File browser header
        header_label = QLabel("📁 Files")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        left_layout.addWidget(header_label)
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory...")
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        left_layout.addLayout(dir_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_file_from_list)
        left_layout.addWidget(self.file_list)
        
        # Create right panel (content area)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        open_btn = QPushButton("📂 Open")
        open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(save_btn)
        
        save_as_btn = QPushButton("📝 Save As")
        save_as_btn.clicked.connect(self.save_as_file)
        toolbar.addWidget(save_as_btn)
        
        toolbar.addStretch()
        
        export_btn = QPushButton("📄 Export HTML")
        export_btn.clicked.connect(self.export_html)
        toolbar.addWidget(export_btn)
        
        # Toggle view button
        self.view_mode = "preview"  # "preview" or "edit"
        toggle_btn = QPushButton("👁️ Toggle View")
        toggle_btn.clicked.connect(self.toggle_view)
        toolbar.addWidget(toggle_btn)
        
        # Reload button
        reload_btn = QPushButton("🔄 Reload")
        reload_btn.clicked.connect(self.reload_file)
        toolbar.addWidget(reload_btn)
        
        right_layout.addLayout(toolbar)
        
        # Create split view
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Edit area
        self.edit_area = QTextEdit()
        self.edit_area.setFont(QFont("Courier New", 11))
        self.edit_area.textChanged.connect(self.update_preview)
        
        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setFont(QFont("Segoe UI", 11))
        self.preview_area.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                padding: 10px;
            }
        """)
        
        self.splitter.addWidget(self.edit_area)
        self.splitter.addWidget(self.preview_area)
        self.splitter.setSizes([600, 600])
        
        right_layout.addWidget(self.splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply styles
        self.apply_styles()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self.close_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        toggle_view_action = QAction("Toggle Preview", self)
        toggle_view_action.setShortcut("Ctrl+T")
        toggle_view_action.triggered.connect(self.toggle_view)
        view_menu.addAction(toggle_view_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        export_html_action = QAction("Export as HTML", self)
        export_html_action.setShortcut("Ctrl+H")
        export_html_action.triggered.connect(self.export_html)
        edit_menu.addAction(export_html_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", 
            QDir.homePath(),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.dir_input.setText(directory)
            self.load_directory(directory)
            
    def load_directory(self, directory):
        self.file_list.clear()
        
        # Watch directory for changes
        if self.watch_directory:
            self.file_watcher.removePath(self.watch_directory)
        
        self.watch_directory = directory
        self.file_watcher.addPath(directory)
        
        # List all markdown files
        md_files = []
        for file in os.listdir(directory):
            if file.endswith(('.md', '.markdown', '.mdown', '.mkd')):
                md_files.append(file)
        
        # Sort files alphabetically
        md_files.sort()
        
        for file in md_files:
            item = QListWidgetItem(f"📄 {file}")
            self.file_list.addItem(item)
            
        self.status_label.setText(f"Loaded {len(md_files)} markdown files from {directory}")
        
    def open_file_from_list(self, item):
        file_name = item.text().replace("📄 ", "")
        if self.watch_directory:
            file_path = os.path.join(self.watch_directory, file_name)
            self.load_file(file_path)
            
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown *.mdown *.mkd);;All Files (*.*)"
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            self.edit_area.setText(content)
            self.current_file = file_path
            self.update_preview()
            
            # Update window title
            self.setWindowTitle(f"Markdown Reader - {os.path.basename(file_path)}")
            self.status_label.setText(f"Loaded: {file_path}")
            
            # Watch file for changes
            if file_path not in self.file_watcher.files():
                self.file_watcher.addPath(file_path)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")
            
    def on_file_changed(self, path):
        """Handle external file changes"""
        if path == self.current_file:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Only update if content is different
                if content != self.edit_area.toPlainText():
                    self.edit_area.setText(content)
                    self.update_preview()
                    self.status_label.setText(f"File updated externally: {path}")
                    
            except Exception as e:
                self.status_label.setText(f"Error reloading file: {str(e)}")
                
    def save_file(self):
        if self.current_file:
            content = self.edit_area.toPlainText()
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_label.setText(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*.*)"
        )
        
        if file_path:
            content = self.edit_area.toPlainText()
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.setWindowTitle(f"Markdown Reader - {os.path.basename(file_path)}")
                self.status_label.setText(f"Saved: {file_path}")
                
                # Watch new file
                if file_path not in self.file_watcher.files():
                    self.file_watcher.addPath(file_path)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                
    def close_file(self):
        self.edit_area.clear()
        self.preview_area.clear()
        self.current_file = None
        self.setWindowTitle("Markdown Reader")
        self.status_label.setText("Closed file")
        
    def reload_file(self):
        if self.current_file:
            self.load_file(self.current_file)
            self.status_label.setText(f"Reloaded: {self.current_file}")
            
    def update_preview(self):
        """Convert markdown to HTML and display in preview"""
        markdown_text = self.edit_area.toPlainText()
        html = markdown.markdown(markdown_text, extensions=['extra', 'codehilite', 'tables'])
        
        # Add CSS styling for better display
        style = """
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
            h2 { color: #2c3e50; border-bottom: 1px solid #ecf0f1; }
            h3 { color: #2c3e50; }
            code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            blockquote { border-left: 4px solid #3498db; padding-left: 20px; margin-left: 0; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #3498db; color: white; }
            img { max-width: 100%; height: auto; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {style}
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        self.preview_area.setHtml(full_html)
        
    def toggle_view(self):
        """Toggle between preview, edit, and split view"""
        if self.view_mode == "preview":
            self.view_mode = "edit"
            self.edit_area.show()
            self.preview_area.hide()
            self.status_label.setText("View: Edit Mode")
        elif self.view_mode == "edit":
            self.view_mode = "split"
            self.edit_area.show()
            self.preview_area.show()
            self.splitter.setSizes([self.width()//2, self.width()//2])
            self.status_label.setText("View: Split Mode")
        else:  # split
            self.view_mode = "preview"
            self.edit_area.hide()
            self.preview_area.show()
            self.status_label.setText("View: Preview Mode")
            
    def export_html(self):
        """Export markdown to HTML file"""
        if not self.edit_area.toPlainText():
            QMessageBox.warning(self, "Warning", "No content to export!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as HTML",
            "",
            "HTML Files (*.html);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Get current HTML from preview
                html_content = self.preview_area.toHtml()
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                self.status_label.setText(f"Exported HTML: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export HTML: {str(e)}")
                
    def show_about(self):
        QMessageBox.about(
            self,
            "About Markdown Reader",
            """
            <h2>Markdown Reader</h2>
            <p>A simple yet powerful markdown reader built with PyQt6.</p>
            <p>Features:</p>
            <ul>
                <li>Real-time markdown preview</li>
                <li>Edit and preview modes</li>
                <li>File browser</li>
                <li>Export to HTML</li>
                <li>File watching for external changes</li>
            </ul>
            <p>Created with ❤️ using Python and PyQt6</p>
            """
        )
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up file watcher
        self.file_watcher.removePaths(self.file_watcher.files())
        if self.watch_directory:
            self.file_watcher.removePath(self.watch_directory)
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    reader = MarkdownReader()
    reader.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()