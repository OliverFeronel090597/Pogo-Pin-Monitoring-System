from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout

from libs.DatabaseConnector import DatabaseConnector


class AddNewHBW(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New BHW")
        self.setFixedSize(200, 100)

        self.database = DatabaseConnector()
        
        layout = QVBoxLayout()

        self.new_bhw = QLineEdit()
        self.new_bhw.setProperty("role", "saveBHW")
        self.new_bhw.textChanged.connect(self.capitalize)

        save_bhw = QPushButton("Save")
        save_bhw.setProperty("role", "saveBHW")
        save_bhw.clicked.connect(self.accept)  # Triggers dialog to close and return Accepted

        layout.addWidget(self.new_bhw)
        layout.addWidget(save_bhw)
        self.setLayout(layout)

    def capitalize(self):
        sender = self.sender()
        sender.setText(sender.text().upper())

    def get_value(self):
        return self.new_bhw.text()
