import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox, QTableWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt, QObject, QEvent


class EditableTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Only start editing on double click
        self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)

        self.setStyleSheet("""
            /* Highlight entire row on hover */
            QTableWidget::item:hover {
                background-color: #C4E1FF;
            }
            /* Highlight entire selected row */
            QTableWidget::item:selected {
                background-color: #a6c8ff;
            }
        """)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.changes = {}

        self.itemChanged.connect(self.mark_changed)

    def mark_changed(self, item):
        row = item.row()
        col = item.column()
        key_item = self.item(row, 0)
        if key_item and key_item.text().strip():
            key = key_item.text()
            header = self.horizontalHeaderItem(col).text()
            value = item.text()
            self.changes[(key, header)] = value


    def mark_changed(self, item):
        row = item.row()
        col = item.column()
        key_item = self.item(row, 0)
        if key_item and key_item.text().strip():
            key = key_item.text()
            header = self.horizontalHeaderItem(col).text()
            value = item.text()
            self.changes[(key, header)] = value


class DataTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POGOINSERTION Editor")
        self.resize(1000, 500)

        self.table = EditableTable()
        self.load_data()

        self.new_rows = []

        self.save_btn = QPushButton("Save")
        self.add_btn = QPushButton("Add Row")
        self.delete_btn = QPushButton("Delete Row")

        self.save_btn.clicked.connect(self.save_changes)
        self.add_btn.clicked.connect(self.add_row)
        self.delete_btn.clicked.connect(self.delete_row)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.save_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.installEventFilter(self)

        # rest of your init code...

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            # If clicked outside the table, clear selection
            if obj is self:
                pos = event.position().toPoint()
                widget_at_pos = self.childAt(pos)
                if widget_at_pos is not self.table and not self.table.isAncestorOf(widget_at_pos):
                    self.table.clearSelection()
        return super().eventFilter(obj, event)

    def load_data(self):
        self.conn = sqlite3.connect(
            r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\DATA\POGOINSERTION.db"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM SAPNUMBER")
        data = self.cursor.fetchall()
        self.headers = [desc[0] for desc in self.cursor.description]

        self.table.setColumnCount(len(self.headers))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(self.headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data) if col_data is not None else "")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()

    def save_changes(self):
        # Validate first
        invalid_entries = []

        for row in range(self.table.rowCount()):
            sap_item = self.table.item(row, 0)
            cost_item = self.table.item(row, 1)

            sap = sap_item.text().strip() if sap_item else ""
            cost = cost_item.text().strip() if cost_item else ""

            if not sap.isdigit():
                invalid_entries.append(f"Row {row + 1}: SAP '{sap}' is not a valid integer.")

            try:
                float(cost)
            except ValueError:
                invalid_entries.append(f"Row {row + 1}: COST '{cost}' is not a valid number.")

        if invalid_entries:
            QMessageBox.warning(self, "Validation Error", "\n".join(invalid_entries))
            return

        # Update existing rows
        for (key, col_name), new_value in self.table.changes.items():
            sql = f"UPDATE SAPNUMBER SET {col_name} = ? WHERE {self.headers[0]} = ?"
            self.cursor.execute(sql, (new_value, key))

        # Insert new rows
        for row in self.new_rows:
            values = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                values.append(item.text() if item else "")

            placeholders = ",".join(["?"] * len(values))
            sql = f"INSERT INTO SAPNUMBER ({', '.join(self.headers)}) VALUES ({placeholders})"
            self.cursor.execute(sql, values)

        self.conn.commit()
        self.table.changes.clear()
        self.new_rows.clear()

        # Print all data rows to console:
        print("Current Table Data:")
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            print(row_data)

        QMessageBox.information(self, "Saved", "Changes saved to database.")

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_position, col, item)
        self.new_rows.append(row_position)

    def delete_row(self):
        selected = self.table.currentRow()
        if selected >= 0:
            sap_value = self.table.item(selected, 0).text()
            confirm = QMessageBox.question(
                self,
                "Delete Row",
                f"Delete row with SAP '{sap_value}' from DB?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.cursor.execute(f"DELETE FROM SAPNUMBER WHERE {self.headers[0]} = ?", (sap_value,))
                self.conn.commit()
                self.table.removeRow(selected)
                if selected in self.new_rows:
                    self.new_rows.remove(selected)
                QMessageBox.information(self, "Deleted", f"Row with SAP '{sap_value}' deleted.")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     viewer = DataTableWidget()
#     viewer.show()
#     sys.exit(app.exec())
