from PyQt6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
import sys

class CustomDropdown(QComboBox):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setEditable(False)  # Make True if you want user to type
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        if items:
            self.addItems(items)

        # Optional: Style
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background: white;
                selection-background-color: #87cefa;
                border: 1px solid lightgray;
            }
        """)

        # Optional: Connect to signal
        self.currentIndexChanged.connect(self.on_selection_changed)

    def on_selection_changed(self, index):
        print(f"Selected index: {index}, value: {self.itemText(index)}")


# 🧪 Sample usage
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Dropdown Example")
        layout = QVBoxLayout(self)

        self.dropdown = CustomDropdown(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(self.dropdown)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(300, 100)
    win.show()
    sys.exit(app.exec())
