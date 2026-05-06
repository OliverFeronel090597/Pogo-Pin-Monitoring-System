from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout)

from libs.DatabaseConnector import DatabaseConnector
from libs.GetUser import get_login_user


class FixUser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fix User")
        self.parentx = parent
        self.database = DatabaseConnector()

        self.main_layout = QVBoxLayout(self)

        # Get E100 user from system login
        self.e100 = get_login_user() or "UNKNOWN"
        self.e100_label = QLabel(f"E100: {self.e100}")
        self.e100_label.setProperty("role", "loginForm")
        self.main_layout.addWidget(self.e100_label)

        # Username input
        username_layout = QHBoxLayout()
        self.main_layout.addLayout(username_layout)

        user_label = QLabel("Username:")
        user_label.setProperty("role", "loginForm")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("J.DOE")
        self.user_input.textChanged.connect(self.capitalize_input)
        username_layout.addWidget(user_label)
        username_layout.addWidget(self.user_input)

        # Submit button
        self.submit_btn = QPushButton("OK")
        self.submit_btn.clicked.connect(self.process_action)
        self.main_layout.addWidget(self.submit_btn)

    def capitalize_input(self):
        text_upper = self.user_input.text().upper()
        self.user_input.setText(text_upper)

    def process_action(self):
        self.database.insert_e100_user(self.e100, self.user_input.text())
        self.parentx.update_username(self.user_input.text())
        self.close()