import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QStyle

app = QApplication([])

# Get the standard icon
icon_enum = QStyle.StandardPixmap.SP_TitleBarMenuButton
icon = app.style().standardIcon(icon_enum)

# Get the QPixmap and save it
pixmap = icon.pixmap(32, 32)
saved = pixmap.save("SP_TitleBarMenuButton.png", "PNG")

if saved:
    print("Icon saved as SP_TitleBarMenuButton.png")
else:
    print("Failed to save icon.")
