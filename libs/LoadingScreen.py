import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QSplashScreen, QProgressBar, QVBoxLayout, QWidget, QLabel, QHBoxLayout

from libs.GlobalVariables import GlobalState
from libs.resources import *


class LoadingSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a pixmap for the splash screen background
        self.splash_width = 800
        self.splash_height = 300
        
        splash_pixmap = QPixmap(self.splash_width, self.splash_height)
        splash_pixmap.fill(Qt.GlobalColor.white)
        
        super().__init__(splash_pixmap)
        
        # Set window flags (frameless and always on top)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Create overlay widgets
        self.overlay_widget = QWidget(self)
        self.overlay_widget.setGeometry(0, 0, self.splash_width, self.splash_height)
        self.overlay_widget.setStyleSheet("background-color: transparent;")
        
        # Main layout for overlay
        layout = QVBoxLayout(self.overlay_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Top layout for images
        top_layout = QVBoxLayout()
        
        # Create a horizontal layout for the two images
        images_layout = QHBoxLayout()
        images_layout.addStretch()
        
        # First image (AMS image)
        self.ams_label = QLabel()
        ams_pixmap = QPixmap(':/resources/image.png').scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio)
        self.ams_label.setPixmap(ams_pixmap)
        images_layout.addWidget(self.ams_label)
        
        images_layout.addStretch()
        
        # Second image (main logo)
        self.image_label = QLabel()
        logo_pixmap = QPixmap(':/resources/main-logo.png').scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(logo_pixmap)
        images_layout.addWidget(self.image_label)
        
        images_layout.addStretch()
        top_layout.addLayout(images_layout)
        layout.addLayout(top_layout)
        
        # Bottom layout for labels
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Author label
        self.author_label = QLabel("AMS Asia")
        self.author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.author_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333333; background-color: transparent;")
        bottom_layout.addWidget(self.author_label)
        
        # Loading label with version
        self.loading_label = QLabel(f"PPM Tool Version {GlobalState.app_version}")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333333; background-color: transparent;")
        bottom_layout.addWidget(self.loading_label)
        
        layout.addLayout(bottom_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                background-color: #f3f3f3;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Ensure overlay is on top
        self.overlay_widget.raise_()
        
        # Set splash screen message styles
        self.setStyleSheet("""
            QSplashScreen {
                background-color: #ffffff;
            }
        """)
    
    def update_progress(self, value, message=""):
        """Update progress bar value and optional message"""
        self.progress_bar.setValue(value)
        if message:
            self.loading_label.setText(message)
        QApplication.processEvents()
    
    def show_message(self, message):
        """Show a message on the splash screen"""
        self.loading_label.setText(message)
        QApplication.processEvents()


def main(ex: QWidget):
    # Create and show splash screen
    loading_screen = LoadingSplashScreen()
    loading_screen.show()
    
    # Process events to ensure splash screen is rendered
    QApplication.processEvents()
    
    progress = 0
    total_steps = 100
    
    def update_progress():
        nonlocal progress
        if progress <= total_steps:
            loading_screen.progress_bar.setValue(progress)
            if progress < 30:
                loading_screen.loading_label.setText(f"Initializing... {progress}%")
            elif progress < 60:
                loading_screen.loading_label.setText(f"Loading modules... {progress}%")
            elif progress < 90:
                loading_screen.loading_label.setText(f"Preparing interface... {progress}%")
            else:
                loading_screen.loading_label.setText(f"Almost ready... {progress}%")
            
            progress += 1
            QApplication.processEvents()
        else:
            loading_timer.stop()
            loading_screen.close()
            ex.show()
    
    # Create timer with 50ms intervals for smooth progress
    loading_timer = QTimer()
    loading_timer.timeout.connect(update_progress)
    loading_timer.start(50)  # Update progress every 50 milliseconds


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PogoPinMonitoring()
    
    # Show splash screen first, then main window
    main(window)
    
    sys.exit(app.exec())