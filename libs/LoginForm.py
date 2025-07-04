from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox
)
from PyQt6.QtGui import QIcon
from libs.DatabaseConnector import DatabaseConnector
from libs.Hasher import hash_password
from libs.GlobalVariables import GlobalState

class LoginDialog(QDialog):
    def __init__(self, function="login", parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(function.capitalize())
        self.function = function  # 'login', 'add', or 'change'
        self.database = DatabaseConnector()
        self.show_password = False

        # Username
        self.username_label = QLabel("Username:")
        self.username_label.setProperty("role", "loginForm")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("username")
        self.username_input.setProperty("role", "loginForm")

        # Password layout
        password_layout = QHBoxLayout()
        password_layout.setSpacing(0)

        self.password_label = QLabel("Password:")
        self.password_label.setProperty("role", "loginForm")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setProperty("role", "showHide")

        self.show_hide = QPushButton()
        self.show_hide.setIcon(QIcon(":/resources/hide.png"))
        self.show_hide.setFixedSize(20, 35)
        self.show_hide.clicked.connect(self.show_hide_password)
        self.show_hide.setProperty("role", "showHide")
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_hide)

        # Confirm password (for add/change)
        self.confirm_label = QLabel("Confirm Password:")
        self.confirm_label.setProperty("role", "loginForm")

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Re-enter password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.hide()
        self.confirm_label.hide()
        self.confirm_input.setProperty("role", "loginForm")

        # Buttons
        self.action_button = QPushButton()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.action_button.setProperty("role", "loginForm")
        self.cancel_button.setProperty("role", "loginForm")

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_label)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(self.confirm_label)
        form_layout.addWidget(self.confirm_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.action_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Customize based on function
        if self.function == "login":
            self.action_button.setText("Login")
            self.action_button.clicked.connect(self.check_login)
        elif self.function == "add":
            self.action_button.setText("Add User")
            self.confirm_label.show()
            self.confirm_input.show()
            self.action_button.clicked.connect(self.add_user)
        elif self.function == "change":
            self.action_button.setText("Change Password")
            self.confirm_label.show()
            self.confirm_input.show()
            self.action_button.clicked.connect(self.change_password)

        self.username_input.setFocus()
        self.setFixedSize(220, 200 if function == "login" else 250)

    def show_hide_password(self):
        if self.show_password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide.setIcon(QIcon(":/resources/hide.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide.setIcon(QIcon(":/resources/show.png"))
        self.show_password = not self.show_password

    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self._show_message("Missing Info", "Please enter both username and password.", QMessageBox.Icon.Warning)
            return

        if self.database.check_user(username, hash_password(password)):
            self._show_message("Login Successful", "Welcome!", QMessageBox.Icon.Information)
            GlobalState.admin_access = True
            self.accept()
        else:
            self._show_message("Login Failed", "Incorrect username or password.", QMessageBox.Icon.Critical)

    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not username or not password or not confirm:
            self._show_message("Missing Info", "Please complete all fields.", QMessageBox.Icon.Warning)
            return

        if password != confirm:
            self._show_message("Mismatch", "Passwords do not match.", QMessageBox.Icon.Warning)
            return

        if self.database.user_exists(username):
            self._show_message("Duplicate", "Username already exists.", QMessageBox.Icon.Critical)
            return

        self.database.add_user(username, hash_password(password))
        self._show_message("Success", "User added successfully.", QMessageBox.Icon.Information)
        self.accept()

    def change_password(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not username or not password or not confirm:
            self._show_message("Missing Info", "Please complete all fields.", QMessageBox.Icon.Warning)
            return

        if password != confirm:
            self._show_message("Mismatch", "Passwords do not match.", QMessageBox.Icon.Warning)
            return

        if not self.database.user_exists(username):
            self._show_message("Not Found", "Username does not exist.", QMessageBox.Icon.Critical)
            return

        self.database.update_password(username, hash_password(password))
        self._show_message("Success", "Password changed successfully.", QMessageBox.Icon.Information)
        self.accept()

    def _show_message(self, title, text, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setProperty("role", "loginForm")
        msg.setText(text)
        msg.setIcon(icon)
        msg.exec()

    # def accept(self):
    #     if self.function=="login":
    #         self.parent.update_login_label(username = self.username_input.text().strip())
    #     return super().accept()