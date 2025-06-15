from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QPushButton,
    QHBoxLayout, QLabel, QMessageBox, QSpacerItem,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt

from libs.CompleterLineEdit import CompleterLineEdit
from libs.DatabaseConnector import DatabaseConnector
from libs.Calendar import CalendarLineEdit
from libs.CustomComboBox import CustomDropdown
from libs.GetRunCount import GetRunCount
from libs.CustomSpinBox import CustomSpinBox
from libs.CustomLineEditNunChar import NumCharLineEdit
from libs.SelectSiteLineEdit import SelectSite
from libs.AutoSuggestTextEdit import SuggestTextEdit
from libs.GetUser import get_login_user


class EditHistoryDialog(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit History")
        # self.resize(600, 600)
        self.setFixedSize(450, 500)

        self.database = DatabaseConnector()
        self.get_run_count = None
        self.pogo_price = 0

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.bhw_name = CompleterLineEdit(self.database.get_all_lb(), 300, self.bhw_valid, parent=self)
        self.bhw_name.setProperty("role", "autoFill")
        self.date_replaced = CalendarLineEdit(min_date_keyword=None, max_date_keyword="today", width=300, parent=self)
        sap_list = self.database.get_sap_number()
        sap_list.insert(0, "")
        self.sap_input = CustomDropdown(sap_list, 300, parent=self)
        self.sap_input.currentIndexChanged.connect(self.get_pogo_price)

        self.run_count = NumCharLineEdit(allow_numbers_only=True, width=300, parent=self)
        self.pogo_pin_use = CustomSpinBox(300, parent=self)
        self.pogo_pin_use.setProperty("role", "CustomSpinBox")
        self.pogo_pin_use.valueChanged.connect(self.calculate_total_price)

        self.total_price = NumCharLineEdit(allow_numbers_only=True, width=300, enable=False, parent=self)
        self.select_site = SelectSite(width=300, parent=self)
        self.login_user = NumCharLineEdit(allow_numbers_only=False, width=300, parent=self)
        self.login_user.setText(get_login_user())
        self.comment = SuggestTextEdit(300, 100, self.database.get_convert_history(), parent=self)

        def add_row(label, widget):
            label_widget = QLabel(label)
            label_widget.setProperty("requiredField", "true")
            form_layout.addRow(label_widget, widget)

        add_row("BHW Name:", self.bhw_name)
        add_row("Date Replaced:", self.date_replaced)
        add_row("SAP Number:", self.sap_input)
        add_row("Run Count:", self.run_count)
        add_row("Qty of Pogo Pin:", self.pogo_pin_use)
        add_row("Price in Euro:", self.total_price)
        add_row("Site's:", self.select_site)
        add_row("Replace By:", self.login_user)
        add_row("Comment:", self.comment)

        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        ok_button = QPushButton("OK")
        ok_button.setProperty("role", "saveButton")
        ok_button.clicked.connect(self.handle_ok)
        cancel_button = QPushButton("Cancel")
        cancel_button.setProperty("role", "saveButton")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        if data:
            self.fill_form(data)

        self.get_pogo_price()

    def fill_form(self, data):
        self.bhw_name.setText(data.get("BHW Name", ""))
        self.date_replaced.setText(data.get("Date Replaced", ""))
        self.sap_input.setCurrentText(data.get("SAP#", ""))
        self.run_count.setText(data.get("Run Count", ""))
        self.pogo_pin_use.setValue(int(data.get("Qty. of Pogo Pins Replaced", 0)))
        self.total_price.setText(data.get("Total Price in Euro", ""))
        self.select_site.setText(data.get("Site/s", ""))
        self.login_user.setText(data.get("Replaced by", ""))
        self.comment.setText(data.get("Remarks", ""))

    def get_pogo_price(self):
        try:
            self.pogo_price = self.database.get_sap_price(self.sap_input.currentText())[0]
        except (IndexError, TypeError):
            self.pogo_price = 0.0

    def calculate_total_price(self):
        try:
            total_price = self.pogo_price * int(self.pogo_pin_use.text())
            self.total_price.setText("{:.2f}".format(total_price))
        except ValueError:
            self.total_price.setText("0.00")

    def bhw_valid(self, bhw):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        if hasattr(self, 'get_run_count') and self.get_run_count is not None and self.get_run_count.isRunning():
            return

        self.get_run_count = GetRunCount(bhw)
        self.get_run_count.message_on_process.connect(lambda msg: self.run_count.setPlaceholderText(msg))
        self.get_run_count.result_runcount.connect(lambda val: self.run_count.setText(val))
        self.get_run_count.finished.connect(QApplication.restoreOverrideCursor)
        self.get_run_count.start()

        last_use_sap = self.database.get_last_use_sap(bhw)
        if last_use_sap:
            index = self.sap_input.findText(last_use_sap, Qt.MatchFlag.MatchExactly)
            if index >= 0:
                self.sap_input.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "SAP Error", "SAP Number not found. Please double-check.")

    def handle_ok(self):
        data_array = [
            self.bhw_name.text(),
            self.date_replaced.text(),
            self.sap_input.currentText(),
            self.run_count.text(),
            self.pogo_pin_use.text(),
            self.total_price.text(),
            self.select_site.text(),
            self.login_user.text(),
            self.comment.toPlainText()
        ]
        print("OK Clicked: ", data_array)
        self.accept()