from PyQt6.QtWidgets import (
    QApplication, QWidget, QFormLayout,
    QLineEdit, QPushButton, QVBoxLayout
)
import sys

class FormExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QFormLayout Sample")

        # Create a form layout
        form_layout = QFormLayout()

        # Add label + input field pairs
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)

        # Add a submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_form)

        # Wrap the form in a vertical layout (optional)
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.submit_button)

        self.setLayout(main_layout)

    def submit_form(self):
        print("Name:", self.name_input.text())
        print("Email:", self.email_input.text())
        print("Password:", self.password_input.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormExample()
    window.show()
    sys.exit(app.exec())
