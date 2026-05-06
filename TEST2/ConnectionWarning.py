import os
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QLabel, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)


class DirectoryChecker(QWidget):
    def __init__(self):
        super().__init__()
        
        self.directory_path = r"\\fsph01\Public\AMS_PHI\12_OPERATIONS\TEST_PRODUCT_ENGINEERING\TPE-Loadboard-Probeshop_Sustaining\Tools\LoadBoardMonitoring\DATA\database\xxxxxx"
        
        self.init_ui()
        
        # Check connection immediately when app starts
        self.check_connection()
        
        # Optionally check periodically (e.g., every 30 seconds)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(30000)  # Check every 30 seconds
    
    def init_ui(self):
        self.setWindowTitle("Directory Connection Monitor")
        self.setGeometry(100, 100, 500, 200)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Checking connection...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        check_button = QPushButton("Check Connection Now")
        check_button.clicked.connect(self.check_connection)
        layout.addWidget(check_button)
        
        self.setLayout(layout)
    
    def check_connection(self):
        """Check if the directory is accessible"""
        if self.is_directory_accessible():
            self.status_label.setText("✓ Connected to directory")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            return True
        else:
            self.status_label.setText("✗ Cannot connect to directory")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.show_warning_popup()
            return False
    
    def is_directory_accessible(self):
        """Check if directory exists and is accessible"""
        try:
            # Try to access the directory
            if os.path.exists(self.directory_path):
                # Try to list contents (optional, more thorough check)
                try:
                    os.listdir(self.directory_path)
                    return True
                except (PermissionError, OSError):
                    return False
            else:
                return False
        except Exception as e:
            print(f"Error checking directory: {e}")
            return False
    
    def show_warning_popup(self):
        """Show a warning message box"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Connection Warning")
        msg_box.setText("Cannot access network directory!")
        msg_box.setInformativeText(
            f"Unable to connect to:\n\n{self.directory_path}\n\n"
            "Please check:\n"
            "• Network connection\n"
            "• VPN connection (if required)\n"
            "• Directory permissions\n"
            "• Server availability"
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | 
                                  QMessageBox.StandardButton.Retry)
        
        # Execute and handle retry
        result = msg_box.exec()
        if result == QMessageBox.StandardButton.Retry:
            self.check_connection()

class SimpleChecker(QWidget):
    """Simpler version that only checks on demand"""
    def __init__(self):
        super().__init__()
        
        self.directory_path = r"\\fsph01\Public\AMS_PHI\12_OPERATIONS\TEST_PRODUCT_ENGINEERING\TPE-Loadboard-Probeshop_Sustaining\Tools\LoadBoardMonitoring\DATA\database"
        
        self.setWindowTitle("Directory Connection Checker")
        self.setGeometry(100, 100, 400, 150)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Click button to check directory connection")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        button = QPushButton("Check Connection")
        button.clicked.connect(self.check_and_notify)
        layout.addWidget(button)
        
        self.setLayout(layout)
    
    def check_and_notify(self):
        """Check connection and show popup if failed"""
        try:
            if os.path.exists(self.directory_path):
                os.listdir(self.directory_path)
                self.label.setText("✓ Connected to directory")
                self.label.setStyleSheet("color: green; font-weight: bold;")
                QMessageBox.information(self, "Success", 
                                       "Successfully connected to directory!")
            else:
                self.show_error_popup()
        except Exception as e:
            print(f"Error: {e}")
            self.show_error_popup()
    
    def show_error_popup(self):
        """Show error message"""
        self.label.setText("✗ Cannot connect to directory")
        self.label.setStyleSheet("color: red; font-weight: bold;")
        
        QMessageBox.critical(
            self,
            "Connection Error",
            f"Cannot access network directory!\n\nPath: {self.directory_path}\n\n"
            "Please check your network connection and permissions."
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Choose which version to run:
    
    # Version 1: Continuous monitoring with periodic checks
    checker = DirectoryChecker()
    checker.show()
    
    # Version 2: Simple on-demand checking (uncomment to use instead)
    # simple_checker = SimpleChecker()
    # simple_checker.show()
    
    sys.exit(app.exec())