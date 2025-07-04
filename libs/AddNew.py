from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem, QLabel, QFormLayout, QSpinBox, QPushButton, QApplication, QMessageBox
from PyQt6.QtCore import Qt

from libs.ImageLabel import ImageLabel
from libs.CompleterLineEdit import CompleterLineEdit
from libs.DatabaseConnector import DatabaseConnector
from libs.Calendar import CalendarLineEdit
from libs.CustomComboBox import CustomDropdown
from libs.GetRunCount import GetRunCount
from libs.CustomLineEditNunChar import NumCharLineEdit
from libs.CustomSpinBox import CustomSpinBox
from libs.SelectSiteLineEdit import SelectSite
from libs.AutoSuggestTextEdit import SuggestTextEdit
from libs.Mailer import MailerThread
from libs.GetUser import get_login_user
from libs.GlobalVariables import GlobalState

class AddNew(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.main_parent = parent
        self.get_run_count = None
        self.pogo_price = 0

        self.database = DatabaseConnector()
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Added margins
        self.main_layout.setSpacing(20)

        self.form_position()
        self.logo_position()

        QLabel("Test")

    def form_position(self):
        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(15)

        # Add form title
        form_title = QLabel("Loadboard Maintenance Form")
        form_title.setProperty("role", "formTitle")
        form_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.addWidget(form_title)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(8)

        # Create widgets
        completer_lb_lst = self.database.get_all_lb()
        self.bhw_name = CompleterLineEdit(completer_lb_lst, 300, self.bhw_valid, parent=self)
        self.bhw_name.setProperty("role", "autoFill")
        # self.bhw_name.completer.activated.connect(self.bhw_valid)
        
        self.date_replaced = CalendarLineEdit(min_date_keyword=None, max_date_keyword="today", width=300, parent=self)

        completer_sap_lst = self.database.get_sap_number()
        completer_sap_lst.insert(0, "")

        self.sap_input = CustomDropdown(completer_sap_lst, 300, parent=self)
        self.sap_input.currentIndexChanged.connect(self.get_pogo_price)

        self.run_count = NumCharLineEdit(allow_numbers_only=True, width=300, parent=self)

        self.pogo_pin_use = CustomSpinBox(300, parent=self)
        self.pogo_pin_use.setProperty("role", "CustomSpinBox")
        self.pogo_pin_use.valueChanged.connect(self.calculate_total_price)

        self.total_price = NumCharLineEdit(allow_numbers_only=True, width=300, enable=False, parent=self)

        self.select_site = SelectSite(width=300, parent=self)
        self.select_site.setReadOnly(True)

        self.login_user = NumCharLineEdit(allow_numbers_only=False, width=300, parent=self)
        self.login_user.textChanged.connect(self.uppercase_login_user)
        self.login_user.setText(get_login_user())
        item = self.database.get_convert_history()

        self.comment = SuggestTextEdit(300, 100, item, parent=self)

        # Helper function to add row and set label property
        def add_row_with_property(label_text, widget, required=False):
            self.add_form_row(form_layout, label_text, widget, required)
            label = form_layout.labelForField(widget)
            label.setProperty("required", "true")

        # Add rows with labels and property
        add_row_with_property("BHW Name :", self.bhw_name, required=True)
        add_row_with_property("Date Replaced:", self.date_replaced, required=True)
        add_row_with_property("SAP Number:", self.sap_input, required=True)
        add_row_with_property("Run Count:", self.run_count, required=True)
        add_row_with_property("Qty of Pogo Pin:", self.pogo_pin_use, required=True)
        add_row_with_property("Price in Euro €:", self.total_price, required=True)
        add_row_with_property("Site's:", self.select_site, required=True)
        add_row_with_property("Replace By:", self.login_user, required=True)
        add_row_with_property("Comment:", self.comment, required=True)

        # Wrap QFormLayout in a QWidget
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        self.form_layout.addWidget(form_widget)

        # Save button
        self.save_layout = QHBoxLayout()
        self.save_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.save_button = QPushButton("Save Record")
        self.save_button.setProperty("role", "saveButton")
        self.save_button.setFixedWidth(200)
        self.save_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_data)
        self.form_layout.addLayout(self.save_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.form_layout.addSpacerItem(spacer)

        self.get_pogo_price()

    def uppercase_login_user(self, text):
        current_cursor_pos = self.login_user.cursorPosition()
        self.login_user.blockSignals(True)  # Prevent recursion
        self.login_user.setText(text.upper())
        self.login_user.setCursorPosition(current_cursor_pos)
        self.login_user.blockSignals(False)

    def add_form_row(self, form_layout, label_text, widget, required=False):
        """Helper method to add a row to the form with styled label"""
        label = QLabel(label_text)
        if required:
            label.setProperty("requiredField", "true")
        form_layout.addRow(label, widget)

    def get_pogo_price(self):
        try:
            self.pogo_price = self.database.get_sap_price(self.sap_input.currentText())
            self.pogo_price = self.pogo_price[0]
        except IndexError as e:
            self.pogo_price = 0.0

    def calculate_total_price(self):
        total_price = self.pogo_price * int(self.pogo_pin_use.text())
        self.total_price.setText("{:.2f}".format(total_price))

    def bhw_valid(self, bhw, func):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        if hasattr(self, 'get_run_count') and self.get_run_count is not None and self.get_run_count.isRunning():
            print("Previous thread is still running")
            return

        self.get_run_count = GetRunCount(bhw)
        self.get_run_count.message_on_process.connect(self.update_runcount_placeholder)
        self.get_run_count.result_runcount.connect(self.update_runcount_value)
        self.get_run_count.finished.connect(QApplication.restoreOverrideCursor)
        self.get_run_count.start()

        last_use_sap = self.database.get_last_use_sap(bhw)
        if last_use_sap:
            index = self.sap_input.findText(last_use_sap, Qt.MatchFlag.MatchExactly)
            if index >= 0:
                self.sap_input.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Sap Error", "Sap Number Not Found.\nPlease double check.")
                print("SAP not in dropdown")
    
    def update_runcount_placeholder(self, msg):
        self.run_count.clear()
        self.run_count.setPlaceholderText(msg)
        "Getting runcount 🔍🔎"

    def update_runcount_value(self, value):
        self.run_count.setPlaceholderText("")
        self.run_count.setText(value)
        if not int(value):
            self.main_parent.show_notification("No runcount found.")

    def logo_position(self):
        self.logo_layout = QVBoxLayout()
        self.logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_layout.setSpacing(2)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.logo_layout)

        self.logo_layout.addSpacing(100)

        self.image_label = ImageLabel(
            ":/resources/image.png",
            self
        )
        self.logo_layout.addWidget(self.image_label)

        self.team_label = QLabel("Test Product Engineering - Loadboard and Probecard Maintenance, Philippines")
        self.team_label.setProperty("role", "teamLabel")
        self.team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.team_label.setWordWrap(True)
        self.logo_layout.addWidget(self.team_label)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.logo_layout.addSpacerItem(spacer)

    def save_data(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        fields = {
            "BHW Name": self.bhw_name.text(),
            "Date Replaced": self.date_replaced.text(),
            "SAP Number": self.sap_input.currentText(),
            "Run Count": self.run_count.text(),
            "Qty of Pogo Pin": self.pogo_pin_use.text(),
            "Price in Euro": self.total_price.text(),
            "Site": self.select_site.text(),
            "Replace By": self.login_user.text(),
            "Comment": self.comment.toPlainText()
        }

        # Flag fields that are empty or contain "0" (or "0.0")
        missing = [
            label for label, value in fields.items()
            if not value.strip() or value.strip() in ("0", "0.0")
        ]



        if missing:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Missing Input", f"Please fill in the following fields:\n\n- " + "\n- ".join(missing))
            return

        QApplication.restoreOverrideCursor()

        print("===== SAVED DATA =====")
        for label, value in fields.items():
            print(f"{label}: {value}")
            
        self.database.insert_history(
            self.bhw_name.text(),
            self.date_replaced.text(),
            self.run_count.text(),
            self.sap_input.currentText(),
            self.pogo_pin_use.text(),
            self.total_price.text(),
            self.select_site.text(),
            self.login_user.text(),
            self.comment.toPlainText()
        )
        self.main_parent.show_notification("Data saved to history.")

        subject = f"Pogo Pin Monitoring Tool Report for {self.bhw_name.text()}"

        message = f"""Hi Team

        Loadboard: {fields['BHW Name']}
        site: {fields['Site']}
        sap_number: {fields['SAP Number']}
        run_count: {fields['Run Count']}
        qty_of_pogo: {fields['Qty of Pogo Pin']}
        price: {fields['Price in Euro']} euro
        replace_by: {fields['Replace By']}
        remarks: {fields['Comment']}

        PPM Version {GlobalState.app_version}
        """
        self.mail_thread = MailerThread(message, "history", subject)
        self.mail_thread.finish_mail.connect(self.on_mail_sent)
        self.mail_thread.start()

        self.bhw_name.clear()
        self.sap_input.setCurrentIndex(0)
        self.run_count.clear()
        self.pogo_pin_use.setValue(0)
        self.total_price.clear()
        self.select_site.clear()
        self.comment.clear()

    def on_mail_sent(self, result: str):
        #QMessageBox.information(self, "Email Result", result)
        self.main_parent.show_notification(result)
        GlobalState.made_changes = True
        print(result)

    def resizeEvent(self, event):
        new_width = int(self.width() / 1.5)
        new_height = int(self.height() / 5)
        self.image_label.resize(new_width, new_height)
        self.image_label.update_pixmap()

        self.setStyleSheet(f'''
            QLabel[role="teamLabel"] {{
                font-size: {int(new_width / 50)}px;
                font-weight: bold;
                color: #2C3E50;
                background-color: transparent;
            }}
        ''')

        super().resizeEvent(event)

        
