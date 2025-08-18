from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication, QVBoxLayout, QSlider, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import (
    Qt, QRectF, QPointF, QTimer, QEasingCurve, QPropertyAnimation, pyqtProperty
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QFont,
    QConicalGradient, QRadialGradient, QPainterPath, QBrush,
    QLinearGradient, QPainterPathStroker, QFontMetrics
)
import sys
import math
import random
from typing import List, Dict, Tuple

class CircularLoadingBar(QWidget):
    def __init__(self):
        super().__init__()
        self._target_value = 0
        self._display_value = 0.0
        self.setMinimumSize(250, 250)
        
        # Animation states
        self._pulse_opacity = 0.35
        self._pulse_direction = 1
        self._shine_angle = 0
        self._bg_hue = 210
        
        # Performance optimizations
        self._cache_enabled = True
        self._backing_store = None
        
        # Particle system
        self._orbit_particles = [
            {'angle': random.uniform(0, 360), 
             'radius_factor': random.uniform(0.9, 1.1), 
             'speed': random.uniform(0.3, 0.8),
             'size': random.uniform(2.5, 3.5)}
            for _ in range(8)
        ]
        
        # Pulse rings state
        self.pulse_rings = [
            {'radius': 0, 'opacity': 0.5, 'speed': 1.4},
            {'radius': 0, 'opacity': 0.3, 'speed': 1.1},
            {'radius': 0, 'opacity': 0.2, 'speed': 0.8},
        ]
        
        # Easing animation
        self.easing = QEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)  # ~33fps
        
        # Font setup
        self._font = QFont("Segoe UI", 1, QFont.Weight.Bold)
        self._font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        
        # Color palette
        self._colors = {
            'primary': QColor(0, 180, 255),
            'secondary': QColor(40, 100, 255),
            'highlight': QColor(100, 200, 255),
            'text': QColor(200, 255, 255),
            'glass': QColor(255, 255, 255, 70),
            'inner_glow': QColor(40, 180, 255, 120),
        }

    def setValue(self, val: int) -> None:
        """Set the target value for the loading bar (0-100)"""
        self._target_value = max(0, min(100, val))
        
    def value(self) -> int:
        """Get the current target value"""
        return self._target_value
        
    def reset(self) -> None:
        """Reset the loading bar to 0"""
        self._target_value = 0
        self._display_value = 0.0
        
    def animate(self) -> None:
        """Update all animation states"""
        # Smooth easing towards target value
        if abs(self._display_value - self._target_value) > 0.1:
            progress = min(abs(self._target_value - self._display_value) / 5, 1)
            easing_value = self.easing.valueForProgress(progress) * 1.5
            self._display_value += easing_value * (1 if self._target_value > self._display_value else -1)
        else:
            self._display_value = self._target_value

        # Pulse effect
        self._pulse_opacity += 0.015 * self._pulse_direction
        if self._pulse_opacity > 0.75:
            self._pulse_direction = -1
        elif self._pulse_opacity < 0.3:
            self._pulse_direction = 1

        # Rotate shine highlight
        self._shine_angle = (self._shine_angle + 1.5) % 360

        # Update particles orbit
        for p in self._orbit_particles:
            p['angle'] = (p['angle'] + p['speed']) % 360

        # Animate background hue
        self._bg_hue = (self._bg_hue + 0.2) % 360

        # Animate pulse rings
        for ring in self.pulse_rings:
            ring['radius'] += ring['speed']
            if ring['radius'] > self.width() / 2:
                ring['radius'] = 0
            ring['opacity'] = max(0, 0.5 * (1 - ring['radius'] / (self.width() / 2)))
            
        self.update()

    def paintEvent(self, event) -> None:
        """Main painting method"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        size = min(self.width(), self.height()) - 20
        center = QPointF(self.width() / 2, self.height() / 2)
        main_rect = QRectF(center.x() - size / 2, center.y() - size / 2, size, size)
        
        # Draw background
        self._draw_background(painter)
        
        # Draw pulse rings behind everything
        self._draw_pulse_rings(painter, center)
        
        # Glassmorphism panel
        self._draw_glass_panel(painter, center, size)
        
        # Outer pulse glow ring
        self._draw_pulse_glow(painter, main_rect)
        
        # Draw progress elements
        self._draw_progress_arc(painter, center, size)
        self._draw_center_circle(painter, center, size)
        self._draw_progress_text(painter)
        
        painter.end()

    def _draw_background(self, painter: QPainter) -> None:
        """Draw the animated background gradient"""
        bg_color1 = QColor.fromHsvF(self._bg_hue / 360, 0.6, 0.1)
        bg_color2 = QColor.fromHsvF(((self._bg_hue + 60) % 360) / 360, 0.7, 0.2)
        bg_grad = QLinearGradient(0, 0, self.width(), self.height())
        bg_grad.setColorAt(0, bg_color1)
        bg_grad.setColorAt(1, bg_color2)
        painter.setBrush(bg_grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def _draw_pulse_rings(self, painter: QPainter, center: QPointF) -> None:
        """Draw the expanding pulse rings"""
        for ring in self.pulse_rings:
            pulse_color = QColor(0, 180, 255, int(255 * ring['opacity']))
            painter.setPen(QPen(pulse_color, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, ring['radius'], ring['radius'])

    def _draw_glass_panel(self, painter: QPainter, center: QPointF, size: float) -> None:
        """Draw the glassmorphism effect panel"""
        glass_rect = QRectF(
            center.x() - size/2 - 10, 
            center.y() - size/2 - 10, 
            size + 20, 
            size + 20
        )
        painter.setBrush(self._colors['glass'])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(glass_rect, 20, 20)

    def _draw_pulse_glow(self, painter: QPainter, rect: QRectF) -> None:
        """Draw the outer pulse glow effect"""
        pulse_pen = QPen(QColor(40, 150, 255, int(255 * self._pulse_opacity)), 30)
        painter.setPen(pulse_pen)
        painter.drawEllipse(rect)

    def _draw_progress_arc(self, painter: QPainter, center: QPointF, size: float) -> None:
        """Draw the main progress arc with all effects"""
        pen_width = 16
        progress_rect = QRectF(
            center.x() - size/2 + pen_width/2,
            center.y() - size/2 + pen_width/2,
            size - pen_width,
            size - pen_width
        )

        # Dynamic gradient that shifts with progress
        dynamic_grad = QConicalGradient(center, -45)
        shift = (self._display_value / 100) * 0.75
        dynamic_grad.setColorAt((0 + shift) % 1, self._colors['primary'])
        dynamic_grad.setColorAt((0.3 + shift) % 1, self._colors['secondary'])
        dynamic_grad.setColorAt((0.6 + shift) % 1, self._colors['highlight'])
        dynamic_grad.setColorAt(1, self._colors['primary'])

        # Main progress arc
        pen_progress = QPen(dynamic_grad, pen_width)
        pen_progress.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_progress)
        
        start_angle = 225 * 16
        span_angle = -int(265 * 16 * (self._display_value / 100))
        painter.drawArc(progress_rect, start_angle, span_angle)

        # Inner glow
        glow_pen = QPen(self._colors['inner_glow'], pen_width + 4)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)
        painter.drawArc(progress_rect, start_angle, span_angle)

        # Rim lighting
        rim_pen = QPen(QColor(200, 230, 255, 40), 1)
        painter.setPen(rim_pen)
        painter.drawEllipse(progress_rect.adjusted(-1, -1, 1, 1))

    def _draw_center_circle(self, painter: QPainter, center: QPointF, size: float) -> None:
        """Draw the center circle with all effects"""
        pen_width = 16
        inner_circle_size = size - pen_width * 2 - 24
        inner_rect = QRectF(
            center.x() - inner_circle_size / 2,
            center.y() - inner_circle_size / 2,
            inner_circle_size,
            inner_circle_size
        )

        # Base circle with radial gradient
        inner_grad = QRadialGradient(center, inner_circle_size / 2)
        inner_grad.setColorAt(0, QColor(40, 40, 60))
        inner_grad.setColorAt(0.85, QColor(10, 10, 15))
        painter.setBrush(inner_grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(inner_rect)

        # Soft white highlight
        highlight_path = QPainterPath()
        highlight_path.addEllipse(inner_rect.adjusted(
            inner_circle_size*0.15, 
            inner_circle_size*0.15,
            -inner_circle_size*0.55, 
            -inner_circle_size*0.55
        ))
        painter.setBrush(QColor(255, 255, 255, 70))
        painter.drawPath(highlight_path)

        # Rotating shine highlight
        shine_path = QPainterPath()
        shine_path.moveTo(center)
        shine_path.arcTo(inner_rect, self._shine_angle, 80)
        shine_path.lineTo(center)
        painter.setBrush(QColor(255, 255, 255, 45))
        painter.drawPath(shine_path)

        # Orbiting particles
        for p in self._orbit_particles:
            angle_rad = math.radians(p['angle'])
            radius = (inner_circle_size / 2) * p['radius_factor']
            x = center.x() + math.cos(angle_rad) * radius
            y = center.y() + math.sin(angle_rad) * radius
            color = QColor(80, 200, 255, 180)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), p['size'], p['size'])

    def _draw_progress_text(self, painter: QPainter) -> None:
        """Draw the progress percentage text with glow effect"""
        progress_text = f"{int(self._display_value)}%"
        
        # Calculate optimal font size based on widget dimensions
        base_size = min(self.width(), self.height()) / 6
        self._font.setPointSizeF(base_size)
        painter.setFont(self._font)
        
        # Text glow layers
        for glow_opacity, offset in [(180, 1), (100, 2), (40, 5)]:
            painter.setPen(QColor(0, 150, 255, glow_opacity))
            painter.drawText(
                self.rect().adjusted(offset, offset, offset, offset),
                Qt.AlignmentFlag.AlignCenter,
                progress_text
            )

        # Main text
        painter.setPen(self._colors['text'])
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, progress_text)

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
from PyQt6.QtWidgets import QWidget


class NetworkStatusIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(180, 200)
        self._connected = True

        # Animation state
        self._pulse_wave_radius = 0
        self._pulse_wave_opacity = 1.0
        self._pulse_opacity = 0.35
        self._pulse_direction = 1
        self._glow_radius = 10
        self._glow_direction = 1
        self._scan_angle = 0

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

        # Colors
        self._colors = {
            'connected': QColor(0, 200, 100),
            'disconnected': QColor(255, 80, 80),
            'text': QColor(240, 240, 240),
            'pulse': QColor(0, 180, 255)
        }

        # Fonts
        self._font = QFont("Segoe UI", 1, QFont.Weight.Bold)
        self._font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

    def setConnected(self, connected: bool) -> None:
        self._connected = connected
        self.update()

    def animate(self) -> None:
        self._pulse_opacity += 0.015 * self._pulse_direction
        if self._pulse_opacity > 0.75:
            self._pulse_direction = -1
        elif self._pulse_opacity < 0.3:
            self._pulse_direction = 1

        self._glow_radius += 0.5 * self._glow_direction
        if self._glow_radius > 15:
            self._glow_direction = -1
        elif self._glow_radius < 5:
            self._glow_direction = 1

        self._scan_angle = (self._scan_angle + 2) % 360

        # Update pulse wave
        self._pulse_wave_radius += 6
        max_radius = max(self.width(), self.height()) * 1.5  # Cover entire widget
        self._pulse_wave_opacity = max(0, 1.0 - self._pulse_wave_radius / max_radius)
        if self._pulse_wave_radius > max_radius:
            self._pulse_wave_radius = 0
            self._pulse_wave_opacity = 1.0

        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width, height = self.width(), self.height()
        center = QPointF(width / 2, height / 2 - 20)

        # Draw expanding pulse that fills the whole widget
        wave_color = QColor(self._colors['pulse'])
        wave_color.setAlphaF(self._pulse_wave_opacity * 0.6)  # Reduce opacity for better visibility
        
        # Draw multiple concentric circles for smoother pulse effect
        for i in range(3):
            radius = max(0, self._pulse_wave_radius - i * 20)
            current_opacity = self._pulse_wave_opacity * (1 - i/3)
            wave_color.setAlphaF(current_opacity * 0.6)
            
            painter.setPen(QPen(wave_color, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius, radius)

        # Main circle and glow
        size = min(width, height - 40) - 30
        main_rect = QRectF(center.x() - size / 2, center.y() - size / 2, size, size)

        # Glow ring
        pulse_pen = QPen(self._colors['pulse'], 8)
        pulse_pen.setColor(QColor(
            self._colors['pulse'].red(),
            self._colors['pulse'].green(),
            self._colors['pulse'].blue(),
            int(255 * self._pulse_opacity)
        ))
        painter.setPen(pulse_pen)
        painter.drawEllipse(main_rect)

        # Rotating scan beam when disconnected
        if not self._connected:
            painter.save()
            painter.translate(center)
            painter.rotate(self._scan_angle)
            beam_color = QColor(0, 255, 255, 80)
            painter.setBrush(beam_color)
            painter.setPen(Qt.PenStyle.NoPen)
            beam_rect = QRectF(-5, -size / 2, 10, size / 2)
            painter.drawEllipse(beam_rect)
            painter.restore()

        # Status circle
        status_color = self._colors['connected'] if self._connected else self._colors['disconnected']
        painter.setPen(QPen(status_color.darker(150), 3))
        painter.setBrush(status_color)
        painter.drawEllipse(center, size / 2 - 10, size / 2 - 10)

        # Status symbol (checkmark or X)
        symbol_size = size * 0.3
        self._font.setPointSizeF(symbol_size)
        painter.setFont(self._font)
        painter.setPen(QColor(255, 255, 255))

        path = QPainterPath()
        if self._connected:
            path.moveTo(center.x() - symbol_size / 2, center.y())
            path.lineTo(center.x() - symbol_size / 6, center.y() + symbol_size / 3)
            path.lineTo(center.x() + symbol_size / 2, center.y() - symbol_size / 3)
        else:
            path.moveTo(center.x() - symbol_size / 2, center.y() - symbol_size / 2)
            path.lineTo(center.x() + symbol_size / 2, center.y() + symbol_size / 2)
            path.moveTo(center.x() + symbol_size / 2, center.y() - symbol_size / 2)
            path.lineTo(center.x() - symbol_size / 2, center.y() + symbol_size / 2)

        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.drawPath(path)

        # Status text
        text_size = size * 0.13
        self._font.setPointSizeF(text_size)
        painter.setFont(self._font)
        painter.setPen(self._colors['text'])
        status_text = "Connected" if self._connected else "Disconnected"

        painter.drawText(
            QRectF(0, center.y() + size / 2 + 10, width, 40),
            Qt.AlignmentFlag.AlignCenter,
            status_text
        )

        painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Separate Loading and Network Indicators")
        self.resize(600, 400)
        
        # Set window styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0066ff, stop:1 #00ccff);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                margin: -5px 0;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 #ffffff, stop:1 #aaddff);
                border-radius: 9px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5555, stop:1 #ff9999);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4444, stop:1 #ff8888);
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # # Left side - Loading bar
        # left_layout = QVBoxLayout()
        # left_layout.setSpacing(20)
        
        # # self.loading_bar = CircularLoadingBar()
        # # left_layout.addWidget(self.loading_bar, 1, Qt.AlignmentFlag.AlignCenter)

        # # self.slider = QSlider(Qt.Orientation.Horizontal)
        # # self.slider.setMinimum(0)
        # # self.slider.setMaximum(100)
        # # self.slider.setValue(0)
        # # self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        # # self.slider.setTickInterval(10)
        # # self.slider.valueChanged.connect(self.loading_bar.setValue)
        # # left_layout.addWidget(self.slider)

        # label = QLabel("Adjust Progress")
        # label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # label.setStyleSheet("""
        #     QLabel {
        #         color: #aaddff; 
        #         font-weight: bold; 
        #         font-size: 14px;
        #         padding: 5px;
        #     }
        # """)
        # left_layout.addWidget(label)
        
        # main_layout.addLayout(left_layout, 1)
        
        # Right side - Network indicator
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        
        self.network_indicator = NetworkStatusIndicator()
        right_layout.addWidget(self.network_indicator, 1, Qt.AlignmentFlag.AlignCenter)
        
        self.network_button = QPushButton("Toggle Network Connection")
        self.network_button.clicked.connect(self.toggle_network)
        right_layout.addWidget(self.network_button)
        
        main_layout.addLayout(right_layout, 1)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def toggle_network(self) -> None:
        """Toggle the network connection state"""
        current_state = not self.network_indicator._connected
        self.network_indicator.setConnected(current_state)
        if current_state:
            self.network_button.setText("Disconnect Network")
        else:
            self.network_button.setText("Reconnect Network")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look
    
    # Set application-wide font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())