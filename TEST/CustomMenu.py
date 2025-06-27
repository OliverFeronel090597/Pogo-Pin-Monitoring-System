from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPixmap
from PyQt6.QtCore import Qt


def red_dot_icon_with_text(text="1", size=16):
    """Create a red dot icon with optional white text inside."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw red circle
    painter.setBrush(QColor("red"))
    painter.setPen(Qt.GlobalColor.transparent)
    painter.drawEllipse(0, 0, size, size)

    # Draw white text centered
    if text:
        painter.setPen(QColor("white"))
        font = QFont("Segoe UI", 8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)

    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Menu with Red Dot")
        self.resize(400, 300)

        # Create menu bar
        menubar = self.menuBar()

        # Add normal File menu
        menubar.addMenu("File")

        # Add System menu with red dot icon
        icon = red_dot_icon_with_text("1", size=14)
        system_menu = QMenu("System", self)
        system_menu.setIcon(icon)
        system_menu.addAction("Settings")
        system_menu.addAction("About")

        menubar.addMenu(system_menu)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
