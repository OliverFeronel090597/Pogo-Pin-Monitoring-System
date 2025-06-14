from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from libs.GlobalVariables import GlobalState

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About PPM')
        #self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint)
        # self.setModal(True)

        # Theme property
        self.setProperty("role", "aboutApp")
        self.style().polish(self)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setProperty("role", "logo")
        logo_pixmap = QPixmap(r'C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\icon\main-logo.png').scaled(
            200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_layout.addWidget(logo_label)
        layout.addLayout(logo_layout)

        # App Info
        app_info = [
            "<h1>Pogo Pin Monitoring</h1>",
            f"<h2>Version: {GlobalState.app_version}</h2>",
            "<h3>Developer: Oliver Feronel</h3>",
            "<h3>Owner: Eduard Caballe</h3>"
        ]
        for info in app_info:
            label = QLabel(info)
            label.setProperty("role", "app_info")
            layout.addWidget(label)

        # License Info
        license_info = [
            '<h3>GUI Qt6: This application uses <a href="https://www.qt.io/licensing">Qt6</a>, available under the LGPLv3 license.</h3>',
            '<h3>LGPL License: This application is licensed under the <a href="https://www.gnu.org/licenses/lgpl-3.0.html">GNU Lesser General Public License v3.0</a>.</h3>',
            '<h3>Language: This application is written in <a href="https://www.python.org/downloads/release/python-3130/">Python 3.13.0 and above</a>.</h3>'
        ]
        for value in license_info:
            label = QLabel(value)
            label.setOpenExternalLinks(True)
            label.setProperty("role", "license")
            layout.addWidget(label)

        # Support Info
        support_info = [
            '<h3>📧 Support: <a href="mailto:oliver.feronel@ams.com" style="color:#1E90FF;">oliver.feronel@ams.com</a></h3>',
        ]

        for value in support_info:
            label = QLabel(value)
            label.setOpenExternalLinks(True)
            label.setProperty("role", "support")
            layout.addWidget(label)
