from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import sys


class ToggleSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setRange(0, 100)
        self.setFixedSize(60, 50)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setValue(0)
        self.is_on = False

        self._animation = QPropertyAnimation(self, b"value", self)
        self._animation.setDuration(400)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.sun_icon = r"C:/Users/O.Feronel/OneDrive - ams OSRAM/Documents/PYTHON/PPM_V5/icon/lightMode.png"
        self.moon_icon = r"C:/Users/O.Feronel/OneDrive - ams OSRAM/Documents/PYTHON/PPM_V5/icon/darkMode.png"

        self.setStyleSheet(self._style(off=True))

    def mousePressEvent(self, event):
        self.toggle()
        super().mousePressEvent(event)

    def toggle(self):
        self.is_on = not self.is_on
        self.setStyleSheet(self._style(off=not self.is_on))
        end_value = 100 if self.is_on else 0
        self._animation.stop()
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(end_value)
        self._animation.start()

    def _style(self, off=True):
        groove_base = "#f8ee5c" if off else "#444444"
        border_highlight = "#ff0000" if off else "#4E6366"
        border_shadow = "#F73232" if off else "#008CFF"
        icon_path = self.sun_icon if off else self.moon_icon
        icon_path = icon_path.replace("\\", "/")

        return f"""
        QSlider::groove:horizontal {{
            background: {groove_base};
            height: 20px;
            border-radius: 10px;
            border: 2px solid transparent;
            background-color: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:0, y2:1,
                stop:0 {border_highlight},
                stop:1 {groove_base}
            );
        }}

        QSlider::handle:horizontal {{
            image: url("{icon_path}");
            width: 26px;
            height: 26px;
            margin: -3px 0;
            border-radius: 13px;
            border: 2px solid {border_shadow};
            background-color: qradialgradient(
                cx:0.5, cy:0.5, radius:0.6,
                fx:0.5, fy:0.5,
                stop:0 {border_highlight},
                stop:1 {groove_base}
            );
        }}
        """


# class DemoWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Curved Embossed Toggle Slider")
#         self.setFixedSize(300, 150)

#         layout = QVBoxLayout(self)

#         self.slider = ToggleSlider()
#         layout.addWidget(self.slider)

#         self.label = QLabel("Mode: Light")
#         self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.addWidget(self.label)

#         self.slider.valueChanged.connect(self.update_label)

#     def update_label(self, value):
#         self.label.setText("Mode: Dark" if self.slider.is_on else "Mode: Light")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = DemoWindow()
#     win.show()
#     sys.exit(app.exec())
