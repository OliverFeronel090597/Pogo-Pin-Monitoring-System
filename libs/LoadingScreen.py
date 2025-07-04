from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

# from libs.CenterWindow import MoveToCenter
from libs.GlobalVariables import GlobalState
from libs.resources import *

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()

        # Set frameless, centered, and always-on-top properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(800, 300)  # Set fixed size for the window
        #MoveToCenter(self)

        # Set icon and title
        self.setWindowTitle("")
        # self.setWindowIcon(QIcon(':/icon/main-logo.png'))

        # Main vertical layout
        main_layout = QVBoxLayout()
        # Top horizontal layout for author and image
        top_layout = QHBoxLayout()
        # top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Image label
        self.ams_label = QLabel()
        self.ams_label.setPixmap(QPixmap(':/resources/image.png').scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio))
        top_layout.addStretch()
        top_layout.addWidget(self.ams_label)

        main_layout.addLayout(top_layout)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap(':/resources/main-logo.png').scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio))
        top_layout.addStretch()
        top_layout.addWidget(self.image_label)

        buttom_layout = QHBoxLayout()
        main_layout.addLayout(buttom_layout)

        # Author label
        self.author_label = QLabel("AMS Asia")
        self.author_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        self.author_label.setStyleSheet("font-weight: bold; font-size: 15px; ")
        buttom_layout.addWidget(self.author_label)

        # Loading label
        self.loading_label = QLabel(f"PPM Tool Version {GlobalState.app_version}")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        buttom_layout.addWidget(self.loading_label)
        
        # Progress bar setup
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                color: black;
                border: 2px solid #3b5998;
                border-radius: 5px;
                background-color: #f3f3f3;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3b5998;
                width: 100px;
            }
        """)

        # Add layouts and widgets to the main layout
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

    # def center_on_screen(self):
    #     screen_geometry = QApplication.primaryScreen().availableGeometry()
    #     x = (screen_geometry.width() - self.width()) // 2
    #     y = (screen_geometry.height() - self.height()) // 2
    #     self.move(x, y)

    # Close window on mouse click
    # def mousePressEvent(self, event):
    #     self.close()



# # Run the application
# app = QApplication([])
# window = LoadingScreen()
# window.show()
# app.exec()
