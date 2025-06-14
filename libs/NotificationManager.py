import sys
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve, QTimer
from PyQt6.QtWidgets import (
     QWidget, QLabel, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QApplication, QStyle
)

class SlideNotification(QFrame):
    def __init__(self, text, parent, icon_name=None, position="left"):
        super().__init__(parent)
        self.position = position
        self.icon_name = icon_name
        self.setProperty("role", "SlideNotification")
        self.setFixedSize(250, 70)

        icon_enum = getattr(QStyle.StandardPixmap, "SP_MessageBoxInformation" if not self.icon_name else self.icon_name)
        icon = QApplication.style().standardIcon(icon_enum)
        pixmap = icon.pixmap(32, 32)


        self.label_icon = QLabel()
        self.label_icon.setPixmap(pixmap)
        self.label_icon.setFixedSize(40, 40)
        self.label_icon.setProperty("role", "SlideNotificationLabel")

        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setProperty("role", "SlideNotificationLabel")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(self.label_icon )
        layout.addWidget(label)

        # Set opacity effect
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        # Fade-in animation
        self.fade_in_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_in_anim.setDuration(600)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)

        # Fade-out animation
        self.fade_out_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_out_anim.setDuration(800)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.finished.connect(self.close)

        # Slide-in animation
        self.pos_anim = QPropertyAnimation(self, b"pos", self)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_anim.setDuration(900)

        # Start fade-out timer
        self.fade_timer = QTimer(self)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self.start_fade_out)

    def animate(self, target_pos):
        # Determine slide-in start position
        if self.position == "left":
            start_pos = QPoint(-self.width(), target_pos.y())
        else:
            start_pos = QPoint(self.parent().width(), target_pos.y())

        self.move(start_pos)
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(target_pos)
        self.pos_anim.start()
        self.fade_in_anim.start()

        # Start fade-out after delay
        self.fade_timer.start(3500)

    def start_fade_out(self):
        self.fade_out_anim.start()

class NotificationManager(QWidget):
    """
    position -> left right

    Icon availble selction, default is SP_MessageBoxInformation

    "SP_TitleBarMenuButton",
    "SP_TitleBarMinButton",
    "SP_TitleBarMaxButton",
    "SP_TitleBarCloseButton",
    "SP_MessageBoxInformation",
    "SP_MessageBoxWarning",
    "SP_MessageBoxCritical",
    "SP_MessageBoxQuestion",
    "SP_ArrowUp",
    "SP_ArrowDown",
    "SP_ArrowLeft",
    "SP_ArrowRight",
    "SP_DirHomeIcon",
    "SP_DirIcon",
    "SP_FileIcon",
    "SP_TrashIcon",
    "SP_DriveHDIcon",
    "SP_DriveFDIcon",
    "SP_DriveCDIcon",
    "SP_ComputerIcon",
    "SP_DesktopIcon",
    "SP_DirOpenIcon",
    "SP_BrowserReload",
    "SP_BrowserStop",
        """

    def __init__(self, parent,icon_name=None, position="left"):
        super().__init__(parent)
        self.notifications = []
        self.icon_name =  icon_name
        self.position = position  # store 'left' or 'right'

    def show_notification(self, message):
        notif = SlideNotification(message, self.parent(), icon_name=self.icon_name, position=self.position)
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
        margin = 25
        base_y = self.parent().height() - margin

        for notif in reversed(self.notifications):
            if self.position == "left":
                x = 15
            else:  # right
                x = self.parent().width() - notif.width() - 15

            notif.move(x, base_y - notif.height())
            base_y -= notif.height() + 3
