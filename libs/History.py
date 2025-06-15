from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidgetItem, QTableWidget, QAbstractItemView,
    QMenu, QHBoxLayout, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt, QEvent, QObject, QTimer
from PyQt6.QtGui import QGuiApplication, QKeySequence

from libs.DatabaseConnector import DatabaseConnector
from libs.CustomSpinBox import CustomSpinBox
from libs.CompleterLineEdit import CompleterLineEdit
from libs.CalendarLineEdit import DateRangeLineEdit
from libs.EditHistory import EditHistoryDialog


class ReadOnlyTable(QTableWidget):
    def __init__(self, headers: list[str], parent=None):
        super().__init__(parent)
        self.headers = headers

        # Read-only and selection behavior
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)

        # Disable manual resizing
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Columns and headers
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setStretchLastSection(True)

        # Enable Ctrl+C for copying selected rows
        self.installEventFilter(self)

    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item:
            menu = QMenu(self)
            print_action = menu.addAction("Edit     ")
            if menu.exec(self.mapToGlobal(pos)) == print_action:
                row = item.row()
                values = [self.item(row, col).text() for col in range(self.columnCount())]
                data = dict(zip(self.headers, values))
                self.edit_history = EditHistoryDialog(data=data, parent=self)
                self.edit_history.exec()

                                # for header, value in data:
                #     print(f"{header}: {value}")
                # print("-" * 40)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection_to_clipboard()
            return True
        return super().eventFilter(obj, event)

    def copy_selection_to_clipboard(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        copied_text = ""
        # Add headers (from left to right column of the first selected range)
        first_range = selected_ranges[0]
        headers = [
            self.horizontalHeaderItem(col).text()
            for col in range(first_range.leftColumn(), first_range.rightColumn() + 1)
        ]
        copied_text += "\t".join(headers) + "\n"
        # Add selected data
        for selection in selected_ranges:
            for row in range(selection.topRow(), selection.bottomRow() + 1):
                row_data = [
                    self.item(row, col).text() if self.item(row, col) else ""
                    for col in range(selection.leftColumn(), selection.rightColumn() + 1)
                ]
                copied_text += "\t".join(row_data) + "\n"
        QGuiApplication.clipboard().setText(copied_text.strip())

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            row = item.row()
            self.clearSelection()
            self.selectRow(row)
        super().mousePressEvent(event)


class History(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.database = DatabaseConnector()

        self.headers = [
            "ID", "BHW Name", "Date Replaced", "Run Count", "SAP#",
            "Qty. of Pogo Pins Replaced", "Total Price in Euro",
            "Site/s", "Replaced by", "Remarks"
        ]

        self.table = ReadOnlyTable(self.headers)

        # Limit with label
        self.limit = CustomSpinBox(width=200, value=100, parent=self)
        self.limit.valueChanged.connect(self.schedule_reload)
        limit_label = QLabel("Limit:")
        limit_label.setMaximumWidth(100)
        limit_label.setProperty("role", "historyLabel")
        self.limit.setProperty("role", "historyInput")

        # BHW data input with label
        completer_lb_lst = self.database.get_all_lb()
        self.bhw_data = CompleterLineEdit(completer_lb_lst, 200, self.load_bhw_history, enter_func=True, parent=self)
        bhw_label = QLabel("BHW Name:")
        bhw_label.setMaximumWidth(100)
        bhw_label.setProperty("role", "historyLabel")
        self.bhw_data.setProperty("role", "historyInput")

        # Date range with label
        self.date_range = DateRangeLineEdit(func=self.load_by_date, parent=self)
       # self.date_range.editingFinished.connect(self.load_by_date)
        date_label = QLabel("Date Range:")
        date_label.setMaximumWidth(100)
        date_label.setProperty("role", "historyLabel")
        self.date_range.setProperty("role", "historyInput")

        # Controls container layout: add all labels and inputs directly
        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        controls_layout.addWidget(limit_label)
        controls_layout.addWidget(self.limit)

        controls_layout.addWidget(bhw_label)
        controls_layout.addWidget(self.bhw_data)

        controls_layout.addWidget(date_label)
        controls_layout.addWidget(self.date_range)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.table)
        main_layout.addLayout(controls_layout)

        self.installEventFilter(self)

        self.reload_timer = QTimer(self)
        self.reload_timer.setSingleShot(True)
        self.reload_timer.timeout.connect(self.reload_table_data)

        self.load_all_history()


    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self and event.type() == QEvent.Type.MouseButtonPress:
            pos = event.position().toPoint()
            widget = self.childAt(pos)
            if not widget or (widget is not self.table and not self.table.isAncestorOf(widget)):
                self.table.clearSelection()
        return super().eventFilter(obj, event)

    def schedule_reload(self):
        self.reload_timer.start(2000)  # Restart 2-second timer

    def reload_table_data(self):
        self.clear_table()
        self.load_all_history()

    def load_all_history(self):
        data = self.database.get_all_history(self.limit.value())
        self.load_data(data)

    def load_data(self, data: list[tuple]):
        # Ensure data is not empty and has consistent length
        if not data:
            return

        # Determine column count from the first row
        column_count = len(data[0])
        self.table.setColumnCount(column_count)
        self.table.setRowCount(len(data))

        # Set table headers (optional – only if you have them predefined)
        if hasattr(self, 'headers'):
            self.table.setHorizontalHeaderLabels(self.headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                display_value = "" if col_data in (None, "", " ") else str(col_data)

                item = QTableWidgetItem(display_value)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

                # Special handling for ID column
                if col_idx == 0:
                    try:
                        item.setData(Qt.ItemDataRole.DisplayRole, int(col_data))
                    except (ValueError, TypeError):
                        item.setData(Qt.ItemDataRole.DisplayRole, 0)

                self.table.setItem(row_idx, col_idx, item)

        # Resize all columns except the last
        for col in range(column_count - 1):
            self.table.resizeColumnToContents(col)

        # Stretch the last column after layout update
        QTimer.singleShot(0, lambda: self.table.horizontalHeader().setStretchLastSection(True))

    def clear_table(self):
        self.table.setRowCount(0)

    def load_bhw_history(self, bhw: str, command=None):
        self.clear_table()
        bhw_history = self.database.get_bhw_history(bhw, command)
        if bhw_history:
            QTimer.singleShot(100, lambda: self.load_data(bhw_history))

    def load_by_date(self):
        # Defensive check for empty or malformed text
        text = self.date_range.text()
        if not text or " - " not in text:
            return
        start_date, end_date = text.split(" - ")
        data_in_range = self.database.get_bhw_history_in_range(start_date, end_date)
        self.clear_table()
        if data_in_range:
            QTimer.singleShot(100, lambda: self.load_data(data_in_range))
