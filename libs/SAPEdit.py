from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidgetItem, QPushButton,
    QHBoxLayout, QMessageBox, QTableWidget, QAbstractItemView,
    QStyledItemDelegate, QLineEdit
)
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from libs.DatabaseConnector import DatabaseConnector
from libs.GlobalVariables import GlobalState


class CellValidatorDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        col = index.column()

        if col == 0:  # SAP Number
            editor = QLineEdit(parent)
            editor.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{0,20}$")))
            return editor
        elif col == 1:  # Price in EURO
            editor = QLineEdit(parent)
            editor.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d*\.?\d{0,10}$")))
            return editor
        return super().createEditor(parent, option, index)


class EditableTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(CellValidatorDelegate(self))
        #self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.SelectedClicked)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        #self.verticalHeader().setVisible(False)
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


class SAPEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.database = DatabaseConnector()
        self.table = EditableTable()
        self.new_rows = []

        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedWidth(300)
        self.add_btn = QPushButton("Add New")
        self.add_btn.setFixedWidth(300)
        self.delete_btn = QPushButton("Delete Row")
        self.delete_btn.setFixedWidth(300)

        self.save_btn.setProperty("role", "sapSave")
        self.add_btn.setProperty("role", "sapAdd")
        self.delete_btn.setProperty("role", "sapDelete")

        self.save_btn.clicked.connect(self.save_changes)
        self.add_btn.clicked.connect(self.add_row)
        self.delete_btn.clicked.connect(self.delete_row)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.installEventFilter(self)
        self.load_data()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress and obj is self:
            pos = event.position().toPoint()
            widget = self.childAt(pos)
            if not widget or (widget is not self.table and not self.table.isAncestorOf(widget)):
                self.table.clearSelection()
        return super().eventFilter(obj, event)

    def load_data(self):
        data = self.database.get_all_sap()
        self.headers = ["SAP Number", "Price in EURO", "Comment", "GET PN", "Winway PN",
                        "Qualmax", "Multitest PN", "FASA/SRM/RASCO/LTX PN", "Joshtech"]

        self.table.setColumnCount(len(self.headers))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(self.headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data) if col_data is not None else "")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()

    def validate_and_collect_row(self, row):
        data_row = []
        is_row_empty = True

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            text = item.text().strip() if item else ""

            if text:  # At least one non-empty cell
                is_row_empty = False

            if col == 0:
                if text and not text.isdigit():
                    raise ValueError(f"Invalid SAP Number at row {row + 1}")
            elif col == 1:
                if text:
                    try:
                        float(text)
                    except ValueError:
                        raise ValueError(f"Invalid Price at row {row + 1}")

            data_row.append(text)

        if is_row_empty:
            raise ValueError(f"Row {row + 1} is completely empty.")

        return data_row

    def save_changes(self):
        try:
            if not GlobalState.admin_access:
                QMessageBox.warning(self, "Access Denied", "Administrator privileges are required to access this feature.\nPlease log in as an admin.")

                return
            
            # First validate all rows
            validated_data = []
            for row in range(self.table.rowCount()):
                data_row = self.validate_and_collect_row(row)
                validated_data.append(data_row)

            # If no exception, proceed to delete and insert
            self.database.delete_all_sap_number()
            for data_row in validated_data:
                self.database.insert_sap_and_details(data_row)

            QMessageBox.information(self, "Saved", "Data saved successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
            print("Validation Error", str(ve))


    def add_row(self):
        if not GlobalState.admin_access:
            QMessageBox.warning(self, "Access Denied", "Administrator privileges are required to access this feature.\nPlease log in as an admin.")

            return
        
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_position, col, item)

        self.new_rows.append(row_position)

    def delete_row(self):
        if not GlobalState.admin_access:
            QMessageBox.warning(self, "Access Denied", "Administrator privileges are required to access this feature.\nPlease log in as an admin.")

            return
        
        selected = self.table.currentRow()
        if selected < 0:
            return

        sap_item = self.table.item(selected, 0)
        if not sap_item:
            return
        sap_value = sap_item.text()

        confirm = QMessageBox.question(
            self,
            "Delete Row",
            f"Delete row with SAP '{sap_value}' from DB?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.database.delete_sap_number(sap_value)
            self.table.removeRow(selected)
            if selected in self.new_rows:
                self.new_rows.remove(selected)
            QMessageBox.information(self, "Deleted", f"Row with SAP '{sap_value}' deleted.")
        else:
            # User canceled deletion, remove highlight/selection
            self.table.clearSelection()
