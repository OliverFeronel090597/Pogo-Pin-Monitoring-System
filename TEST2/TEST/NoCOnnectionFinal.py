from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton
import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
from math import sin, pi

class NetworkStatusIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 300)
        self._connected = True
        self._waves = []
        self._wave_interval = 15
        self._wave_timer = 0

        self._rotation_angle = 0  # rotation angle for arc animation
        self._x_wave_phase = 0    # phase for X animation

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        if not self._connected:
            max_radius = (self.width() ** 2 + self.height() ** 2) ** 0.5
            self._wave_timer += 1
            self._rotation_angle = (self._rotation_angle + 5) % 360  # rotate arc
            self._x_wave_phase += 0.2  # speed of wave animation for X
            
            if self._wave_timer >= self._wave_interval:
                self._waves.append({'radius': 0, 'opacity': 1.0})
                self._wave_timer = 0

            new_waves = []
            for wave in self._waves:
                wave['radius'] += 4
                wave['opacity'] = max(0.0, 1.0 - wave['radius'] / max_radius)
                if wave['opacity'] > 0:
                    new_waves.append(wave)
            self._waves = new_waves
            self.update()
        else:
            # When connected, keep rotation angle fixed (optional)
            self._rotation_angle = 0
            self._x_wave_phase = 0  # reset animation phase when connected

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        center = QPointF(w / 2, h / 2)
        painter.fillRect(self.rect(), QColor("#111"))

        if not self._connected:
            # Draw pulse waves only when disconnected
            for wave in self._waves:
                color = QColor(255, 80, 80)
                color.setAlphaF(wave['opacity'] * 0.5)
                painter.setPen(QPen(color, 3))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center, wave['radius'], wave['radius'])

            # Draw rotating arc only when disconnected
            size = min(w, h) / 4
            arc_radius = size / 2 + 6
            pen = QPen(QColor(255, 80, 80, 160), 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            start_angle = self._rotation_angle * 16
            span_angle = 90 * 16
            painter.drawArc(
                int(center.x() - arc_radius), int(center.y() - arc_radius),
                int(arc_radius * 2), int(arc_radius * 2),
                start_angle, span_angle
            )

        # --- Main status circle ---
        size = min(w, h) / 4
        status_color = QColor(0, 200, 100) if self._connected else QColor(255, 80, 80)
        painter.setPen(QPen(status_color.darker(150), 4))
        painter.setBrush(status_color)
        painter.drawEllipse(center, size / 2, size / 2)

        # --- Center icon ---
        painter.setPen(QPen(Qt.GlobalColor.white, 4))
        path = QPainterPath()

        if self._connected:
            # Checkmark (no animation needed here)
            path.moveTo(center.x() - 10, center.y())
            path.lineTo(center.x() - 2, center.y() + 8)
            path.lineTo(center.x() + 12, center.y() - 8)
        else:
            # X mark with wave animation horizontally
            wave_amplitude = 5
            wave_offset = sin(self._x_wave_phase) * wave_amplitude

            # First line of X
            path.moveTo(center.x() - 10 + wave_offset, center.y() - 10)
            path.lineTo(center.x() + 10 + wave_offset, center.y() + 10)
            # Second line of X
            path.moveTo(center.x() + 10 + wave_offset, center.y() - 10)
            path.lineTo(center.x() - 10 + wave_offset, center.y() + 10)

        painter.drawPath(path)

        # --- Status text ---
        painter.setPen(QColor(220, 220, 220))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            0, h - 40, w, 30,
            Qt.AlignmentFlag.AlignCenter,
            "Connected" if self._connected else "Disconnected"
        )



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulse Only When Disconnected")
        self.resize(500, 500)

        layout = QVBoxLayout()
        self.pulse_widget = NetworkStatusIndicator()
        self.toggle_btn = QPushButton("Toggle Status")
        self.toggle_btn.clicked.connect(self.toggle_status)

        layout.addWidget(self.pulse_widget)
        layout.addWidget(self.toggle_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_status(self):
        self.pulse_widget.setConnected(not self.pulse_widget._connected)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
