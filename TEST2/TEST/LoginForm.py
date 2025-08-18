from PyQt6.QtWidgets import (
    QApplication, QDialog, QLineEdit, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
import sys

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(300, 150)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Login")
        self.cancel_button = QPushButton("Cancel")

        self.login_button.clicked.connect(self.check_login)
        self.cancel_button.clicked.connect(self.reject)

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Dummy check
        if username == "admin" and password == "1234":
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")


# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = LoginDialog()

    if dialog.exec():
        print("Login successful")
    else:
        print("Login canceled")

    sys.exit()
