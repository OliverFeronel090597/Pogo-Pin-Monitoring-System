import sys
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer, Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        label = QLabel("This is the main app window.")
        layout.addWidget(label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


class TrayApp:
    def __init__(self, app):
        self.app = app
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme(r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\icon\image copy.png"))  # Use any icon or provide a .png path

        # Setup reminder timer
        self.timer = QTimer()
        self.timer.setInterval(10000)  # 10 seconds
        self.timer.timeout.connect(self.show_reminder)

        self.window = MainWindow()

        # Create tray menu
        self.menu = QMenu()

        self.show_action = QAction("Show App")
        self.show_action.triggered.connect(self.window.show)
        self.menu.addAction(self.show_action)

        self.start_reminder_action = QAction("Start Reminder")
        self.start_reminder_action.triggered.connect(self.start_reminder)
        self.menu.addAction(self.start_reminder_action)

        self.stop_reminder_action = QAction("Stop Reminder")
        self.stop_reminder_action.triggered.connect(self.stop_reminder)
        self.stop_reminder_action.setEnabled(False)
        self.menu.addAction(self.stop_reminder_action)

        exit_action = QAction("Exit")
        exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.setToolTip("Reminder App Running")
        self.tray_icon.show()

    def start_reminder(self):
        self.timer.start()
        self.start_reminder_action.setEnabled(False)
        self.stop_reminder_action.setEnabled(True)
        self.tray_icon.showMessage("Reminder Started", "You'll get a reminder every 10 seconds.", QSystemTrayIcon.MessageIcon.Information)

    def stop_reminder(self):
        self.timer.stop()
        self.start_reminder_action.setEnabled(True)
        self.stop_reminder_action.setEnabled(False)
        self.tray_icon.showMessage("Reminder Stopped", "No more reminders.", QSystemTrayIcon.MessageIcon.Information)

    def show_reminder(self):
        # Optional: replace this with popup or log
        self.tray_icon.showMessage("Reminder", "Hey! It's time to take a break!", QSystemTrayIcon.MessageIcon.Warning)

    def quit_app(self):
        self.timer.stop()
        self.tray_icon.hide()
        self.app.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Allow running in tray only

    tray_app = TrayApp(app)
    sys.exit(app.exec())
