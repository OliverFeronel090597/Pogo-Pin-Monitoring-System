from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame, QLabel, QMessageBox, QPushButton
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QTimer
import datetime
import sys
import time
import os
import shutil


from libs.resources import *
from libs.DatabaseConnector import DatabaseConnector
from libs.StyleUtils import apply_stylesheet
from libs.GetUser import get_login_user
from libs.GlobalVariables import GlobalState
from libs.ControlButtons import ControlButton
from libs.CustomSlider import ToggleSlider
from libs.AddNew import AddNew
from libs.SAPEdit import SAPEdit
from libs.History import History
from libs.NotificationManager import NotificationManager
from libs.LoginForm import LoginDialog
from libs.About import AboutDialog
from libs.DataGraphing import DataGraphing
from libs.LoadingScreen import LoadingScreen


class PogoPinMonitoring(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = DatabaseConnector()
        self.database.create_tables_if_not_exist()

        self._init_modules()
        self._init_ui()
        self._create_menu()
        self._create_taskbar()

        apply_stylesheet(self, ":/resources/light.qss")

    def _init_modules(self):
        self.slider_switch = ToggleSlider(parent=self)
        self.add_new = AddNew(self)
        self.sap_edit = SAPEdit(self)
        self.histoty = History(self)
        self.data_graphing = DataGraphing(self)
        self.last_clicked_button = None

    def _init_ui(self):
        self.setWindowTitle("Pogo Pin Monitoring BETA")
        self.setWindowIcon(QIcon(":/resources/main-logo.png"))
        self.setMinimumSize(1100, 780)
        self.resize(1000, 780)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        #self.header_anouncement()
        self._create_controls()
        self._create_separator()
        self._create_stack_widget()

        self.notification_manager = NotificationManager(self.main_widget, position="right")

        # Set default page
        self.on_button_click(self.add_new_button, self.stack_widget, 0)
        #QTimer.singleShot(5000, self.version_check)

    def header_anouncement(self):
        self.announcement_layout = QHBoxLayout()
        self.main_layout.addLayout(self.announcement_layout)

        self.announcement_label = QLabel("Anouncement")
        self.announcement_label.setProperty("role", "anouncement")
        self.announcement_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.announcement_layout.addWidget(self.announcement_label)

    def _create_controls(self):
        self.control_layout = QHBoxLayout()
        self.control_layout.setSpacing(1)
        self.control_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addLayout(self.control_layout)

        # Buttons
        self.add_new_button = ControlButton(name="New Item")
        self.sap_button = ControlButton(name="SAP")
        self.history_button = ControlButton(name="History")
        self.data_extract_button = ControlButton(name="Extract Data")

        # Connect buttons
        self.add_new_button.clicked.connect(lambda: self.on_button_click(self.add_new_button, self.stack_widget, 0))
        self.sap_button.clicked.connect(lambda: self.on_button_click(self.sap_button, self.stack_widget, 1))
        self.history_button.clicked.connect(lambda: self.on_button_click(self.history_button, self.stack_widget, 2))
        self.data_extract_button.clicked.connect(lambda: self.on_button_click(self.data_extract_button, self.stack_widget, 3))

        # Add to layout
        self.control_layout.addWidget(self.add_new_button)
        self.control_layout.addWidget(self.sap_button)
        self.control_layout.addWidget(self.history_button)
        self.control_layout.addWidget(self.data_extract_button)

        # Mode toggle on the right
        self.mode_layout = QHBoxLayout()
        self.mode_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.control_layout.addLayout(self.mode_layout)
        self.mode_layout.addWidget(self.slider_switch)

        self.slider_switch.valueChanged.connect(self.update_theme)

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setProperty("role", "UnderlineSeperator")
        self.main_layout.addWidget(line)

    def _create_stack_widget(self):
        self.stack_widget = QStackedWidget()
        self.stack_widget.addWidget(self.add_new)
        self.stack_widget.addWidget(self.sap_edit)
        self.stack_widget.addWidget(self.histoty)
        self.stack_widget.addWidget(self.data_graphing)
        self.stack_widget.setCurrentIndex(0)
        self.main_layout.addWidget(self.stack_widget)

    def _create_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        about_action = QAction("About       ", self)
        about_action.triggered.connect(self.open_about_app)
        file_menu.addAction(about_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # System Menu
        menu_title = "System" if not self.version_check(True) else "System 🔴"
        system_menu = menubar.addMenu(menu_title)
        check_update_action = QAction("Check for Updates", self)
        check_update_action.triggered.connect(self.version_check)
        system_menu.addAction(check_update_action)

        # Account Menu
        account_menu = menubar.addMenu("Account")
        login_action = QAction("Login", self)
        login_action.triggered.connect(lambda: self.acount_dialog("login"))
        account_menu.addAction(login_action)

        change_action = QAction("Change Password", self)
        change_action.triggered.connect(lambda: self.acount_dialog("change"))
        account_menu.addAction(change_action)

        new_action = QAction("New User", self)
        new_action.triggered.connect(lambda: self.acount_dialog("add"))
        account_menu.addAction(new_action)

    def _create_taskbar(self):
        self.taskbar_layout = QHBoxLayout()
        self.main_layout.addLayout(self.taskbar_layout)

        self.app_name = QLabel(f"Pogo Pin Monitoring V{GlobalState.app_version} Beta")
        self.comp_name = QLabel("AMS Asia .inc")
        self.pc_login_name = QLabel(f"Basic User: {get_login_user().upper()}")
        self.dev_name = QLabel("Contact: oliver.feronel@ams.com")
        self.dev_name.setAlignment(Qt.AlignmentFlag.AlignRight)

        for label in [self.app_name, self.comp_name, self.pc_login_name, self.dev_name]:
            label.setProperty("role", "taskBar")
            self.taskbar_layout.addWidget(label)

    def on_button_click(self, button: QWidget, stack: QStackedWidget, index: int):
        if self.last_clicked_button and self.last_clicked_button != button:
            self.last_clicked_button.highlight(False)

        button.highlight(True)
        self.last_clicked_button = button
        stack.setCurrentIndex(index)

    def update_theme(self, value: int):
        if value == 100:
            apply_stylesheet(self, ':/resources/dark.qss')
            self.slider_switch.setEnabled(True)
        elif value == 0:
            apply_stylesheet(self, ':/resources/light.qss')
            self.slider_switch.setEnabled(True)
        else:
            self.slider_switch.setEnabled(False)

    def show_notification(self, message: str):
        self.notification_manager.show_notification(message)

    def acount_dialog(self, func: str):
        login = LoginDialog(function=func , parent=self)
        if login.exec() and func == "login":
            self.pc_login_name.setText(f"Admin User: {get_login_user().upper()}")
    
    def open_about_app(self):
        self.about_app = AboutDialog(parent=self)
        self.about_app.exec()

    def version_check(self, sys_check=False):
        version = GlobalState.app_version
        is_old_version = self.database.check_version(version)
        if sys_check:
            return is_old_version
        
        # print(is_old_version)
        if not is_old_version:
            self.show_notification("Application is up to date.")
        else:
            self.show_notification("Application is outdated.")

    def delete_old_files_in_directory(self):
        directory_paths = GlobalState.backup_directory_path  # Get the list of directories

        if not isinstance(directory_paths, list):
            print("ERROR: GlobalVariable.backup_directory_path should be a list.")
            return

        current_time = time.time()
        one_week_in_seconds = 7 * 24 * 60 * 60  # 7 days in seconds

        for directory_path in directory_paths:
            if not isinstance(directory_path, (str, bytes, os.PathLike)):
                print(f"ERROR: Invalid path {directory_path}. Skipping...")
                continue

            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                for filename in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, filename)

                    if os.path.isfile(file_path):
                        last_modified_time = os.path.getmtime(file_path)
                        file_age_in_seconds = current_time - last_modified_time

                        if file_age_in_seconds > one_week_in_seconds:
                            print(f"Deleting old file: {file_path}")
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        else:
                            print(f"File {file_path} is not old enough to delete.")
            else:
                print(f"WARNING: The directory {directory_path} does not exist.")

    def backup_data(self):
        if not GlobalState.made_changes:
            return
        self.delete_old_files_in_directory()
        newname = datetime.datetime.now().strftime("%Y-%m-%d")
        source_path = os.path.join(GlobalState.database_path, "POGOINSERTION.db")
        backup_directory = GlobalState.backup_directory_path
        print(backup_directory)

        for i, directory in enumerate(backup_directory):
            # Make sure the directory exists
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Construct the target path for the backup
            base_name = os.path.basename(source_path)
            newnamebackup = f'{newname}_{base_name}' if i == 1 else base_name
            backup_path = os.path.join(directory, newnamebackup)

            try:
                shutil.copy(source_path, backup_path)
                print(f'Backup created at: {backup_path}')
            except Exception as e:
                print(f'Failed to backup to {backup_path}: {e}')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.notification_manager.reposition_notifications()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        self.backup_data()
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main(ex : QWidget):
    loading_screen = LoadingScreen()
    loading_screen.show()

    progress = 0
    total_steps = 100
    progress_step = 5

    def update_progress():
        nonlocal progress
        if progress <= total_steps :
            loading_screen.progress_bar.setValue(progress)
            progress += progress_step
        else:
            loading_timer.stop()
            loading_screen.close()
            ex.show()

    loading_timer = QTimer()
    loading_timer.timeout.connect(update_progress)
    loading_timer.start(50)  # Update progress every 50 milliseconds

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PogoPinMonitoring()
    main(window)
    sys.exit(app.exec())
