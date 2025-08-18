import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QCompleter
)
from PyQt6.QtCore import Qt, QStringListModel

class LightCompleterDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QCompleter Light Mode Demo")
        self.resize(400, 100)

        # Sample suggestions
        suggestions = [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon",
            "Zeta", "Eta", "Theta", "Iota", "Kappa"
        ]

        # Setup input
        self.input = QLineEdit()
        self.input.setPlaceholderText("Start typing...")

        # Setup completer
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.input.setCompleter(completer)

        # Style the completer's popup (QListView)
        completer.popup().setStyleSheet("""
            QListView {
                background-color: #ffffff;
                color: #2C3E50;
                border: 1px solid #ccc;
                padding: 4px;
                font: 10pt "Segoe UI";
            }

            QListView::item {
                height: 24px;
                padding-left: 8px;
            }

            QListView::item:hover {
                background-color: #D6EAF8;
                color: #000000;
            }

            QScrollBar:vertical {
                background: #f2f2f2;
                width: 10px;
                margin: 2px 0;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #95A5A6;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LightCompleterDemo()
    window.show()
    sys.exit(app.exec())
