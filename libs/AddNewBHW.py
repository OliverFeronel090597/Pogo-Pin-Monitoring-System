from PyQt6.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QPushButton

class AddNewHBW(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("New BHW")
        self.setFixedSize(200, 100)

        layout = QVBoxLayout()
        
        new_bhw = QLineEdit()
        new_bhw.setProperty("role", "saveBHW")
        new_bhw.textChanged.connect(self.capitalize)

        save_bhw = QPushButton("Save")
        save_bhw.setProperty("role", "saveBHW")



        layout.addWidget(new_bhw)
        layout.addWidget(save_bhw)
        self.setLayout(layout)
        
    def capitalize(self):
        sender = self.sender()
        sender.setText(sender.text().upper())