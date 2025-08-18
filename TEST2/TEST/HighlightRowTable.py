from PyQt6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QMainWindow
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor
import sys


class HoverTable(QTableWidget):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)
        self.last_hovered_row = -1

        # Table appearance setup
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(False)
        self.setStyleSheet("QTableWidget::item:hover { background-color: transparent; }")  # Disable default hover
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

        # Fill with data
        for row in range(rows):
            for col in range(cols):
                self.setItem(row, col, QTableWidgetItem(f"R{row+1}, C{col+1}"))

    def eventFilter(self, obj, event):
        if obj == self.viewport():
            if event.type() == QEvent.Type.MouseMove:
                index = self.indexAt(event.pos())
                if index.isValid():
                    row = index.row()
                    if row != self.last_hovered_row:
                        self.clear_hover()
                        self.last_hovered_row = row
                        self.highlight_row(row)
            elif event.type() == QEvent.Type.Leave:
                self.clear_hover()
                self.last_hovered_row = -1
        return super().eventFilter(obj, event)

    def highlight_row(self, row):
        hover_color = QColor("#c2e7ff")
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(hover_color)

    def clear_hover(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setBackground(QColor("white"))  # Or default background


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hover Highlight Full Row - Same Color")
        self.resize(600, 400)
        self.table = HoverTable(10, 4)
        self.setCentralWidget(self.table)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
