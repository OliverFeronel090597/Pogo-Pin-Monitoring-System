import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QFrame, QGraphicsOpacityEffect
)

class SlideNotification(QFrame):
    def __init__(self, text, parent):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #444;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.setFixedSize(250, 60)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(label)

        # Opacity for fade-in
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_anim.setDuration(600)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)

        self.pos_anim = QPropertyAnimation(self, b"pos", self)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_anim.setDuration(600)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)

    def animate(self, target_pos):
        start_pos = QPoint(-self.width(), target_pos.y())
        self.move(start_pos)
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(target_pos)
        self.pos_anim.start()
        self.fade_anim.start()
        self.timer.start(4000)

class NotificationManager(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.notifications = []

    def show_notification(self, message):
        notif = SlideNotification(message, self.parent())
        self.notifications.append(notif)
        notif.show()
        self.reposition_notifications()
        notif.animate(notif.pos())

        QTimer.singleShot(4100, lambda: self.cleanup(notif))

    def cleanup(self, notif):
        if notif in self.notifications:
            self.notifications.remove(notif)
            notif.deleteLater()
            self.reposition_notifications()

    def reposition_notifications(self):
        margin = 10
        base_x = margin
        base_y = self.parent().height() - margin
        for notif in reversed(self.notifications):  # newest on top
            notif.move(base_x, base_y - notif.height())
            base_y -= notif.height() + margin

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smooth Slide Notification")
        self.resize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        btn = QPushButton("Show Notification")
        btn.clicked.connect(self.show_notification)
        layout.addWidget(btn)
        layout.addStretch()

        self.notifier = NotificationManager(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.notifier.reposition_notifications()

    def show_notification(self):
        self.notifier.show_notification("🔔 Message received successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
