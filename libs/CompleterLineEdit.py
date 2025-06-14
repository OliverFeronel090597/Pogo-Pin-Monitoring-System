from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtCore import Qt, QStringListModel

class CompleterLineEdit(QLineEdit):
    def __init__(self, suggestions, width, func, enter_func=False, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.enter_func = enter_func
        self.setMaximumWidth(width)
        self.suggestions = suggestions
        self.enter_callback = func  # Save the function to call on Enter

        self.completer = QCompleter()
        self.completer.setModel(QStringListModel(self.suggestions))
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self.completer)

        # Connect signal for when a suggestion is selected
        self.completer.activated.connect(self.enter_callback)

    def focusOutEvent(self, a0):
        text = self.text()
        if text not in self.suggestions and not self.enter_func:
            self.clear()
        return super().focusOutEvent(a0)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not self.enter_func or not self.text():
                return
            if self.enter_callback:
                self.enter_callback(self.text(), "like")  # Call function with current text
        super().keyPressEvent(event)
