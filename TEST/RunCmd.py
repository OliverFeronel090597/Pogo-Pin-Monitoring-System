import subprocess
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit

class CommandRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CMD Runner")

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.run_btn = QPushButton("Run Command")
        self.run_btn.clicked.connect(lambda: self.run_cmd('dir'))

        layout = QVBoxLayout()
        layout.addWidget(self.output)
        layout.addWidget(self.run_btn)
        self.setLayout(layout)

    def run_cmd(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            self.output.append(result.stdout if result.returncode == 0 else result.stderr)
        except Exception as e:
            self.output.setText(str(e))


if __name__ == "__main__":
    app = QApplication([])
    win = CommandRunner()
    win.show()
    app.exec()
