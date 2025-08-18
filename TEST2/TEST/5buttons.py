import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import QTimer

class ButtonProcessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button Process Example")
        self.setGeometry(100, 100, 300, 200)

        self.buttons = []
        layout = QVBoxLayout(self)

        for i in range(5):
            btn = QPushButton(f"Button {i + 1}")
            btn.clicked.connect(lambda _, b=btn: self.handle_button_click(b))
            layout.addWidget(btn)
            self.buttons.append(btn)

        self.default_style = self.buttons[0].styleSheet()
        self.process_style = "background-color: lightgreen;"

        # Auto-select first button on start
        QTimer.singleShot(100, lambda: self.handle_button_click(self.buttons[0]))

    def handle_button_click(self, clicked_button):
        for btn in self.buttons:
            if btn == clicked_button:
                btn.setStyleSheet(self.process_style)
            else:
                btn.setStyleSheet(self.default_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ButtonProcessApp()
    window.show()
    sys.exit(app.exec())
