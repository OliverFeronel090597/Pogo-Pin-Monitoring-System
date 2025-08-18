from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication, QVBoxLayout, QSlider, QLabel
)
from PyQt6.QtCore import (
    Qt, QRectF, QPointF, QTimer, QEasingCurve, QTimer
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QFont,
    QConicalGradient, QRadialGradient, QPainterPath, QBrush,
    QLinearGradient, QPainterPathStroker, QFontMetrics
)
import time
import sys
import math
import random
from typing import List, Dict

class CircularLoadingBar(QWidget):
    def __init__(self):
        super().__init__()
        self._target_value = 0
        self._display_value = 0.0  # For smooth easing animation
        self.setMinimumSize(350, 350)
        
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
            for _ in range(8)  # Reduced from 12 for better performance
        ]
        
        # Pulse rings state
        self.pulse_rings = [
            {'radius': 0, 'opacity': 0.5, 'speed': 1.4},
            {'radius': 0, 'opacity': 0.3, 'speed': 1.1},
            {'radius': 0, 'opacity': 0.2, 'speed': 0.8},
        ]
        
        # Easing animation for smoother transitions
        self.easing = QEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)  # ~33fps (reduced from 40fps for better performance)
        
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
            'inner_glow': QColor(40, 180, 255, 120)
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
        self._shine_angle = (self._shine_angle + 1.5) % 360  # Slowed down slightly

        # Update particles orbit
        for p in self._orbit_particles:
            p['angle'] = (p['angle'] + p['speed']) % 360

        # Animate background hue slowly cycling
        self._bg_hue = (self._bg_hue + 0.2) % 360  # Slowed down

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
        
        size = min(self.width(), self.height()) - 50
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
        
        # Main progress arc
        self._draw_progress_arc(painter, center, size)
        
        # Center circle with effects
        self._draw_center_circle(painter, center, size)
        
        # Progress text
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
            center.x() - size/2 - 20, 
            center.y() - size/2 - 20, 
            size + 40, 
            size + 40
        )
        painter.setBrush(self._colors['glass'])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(glass_rect, 40, 40)

    def _draw_pulse_glow(self, painter: QPainter, rect: QRectF) -> None:
        """Draw the outer pulse glow effect"""
        pulse_pen = QPen(QColor(40, 150, 255, int(255 * self._pulse_opacity)), 48)
        painter.setPen(pulse_pen)
        painter.drawEllipse(rect)

    def _draw_progress_arc(self, painter: QPainter, center: QPointF, size: float) -> None:
        """Draw the main progress arc with all effects"""
        pen_width = 22
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
        glow_pen = QPen(self._colors['inner_glow'], pen_width + 6)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)
        painter.drawArc(progress_rect, start_angle, span_angle)

        # Rim lighting
        rim_pen = QPen(QColor(200, 230, 255, 40), 2)
        painter.setPen(rim_pen)
        painter.drawEllipse(progress_rect.adjusted(-1, -1, 1, 1))

    def _draw_center_circle(self, painter: QPainter, center: QPointF, size: float) -> None:
        """Draw the center circle with all effects"""
        pen_width = 22
        inner_circle_size = size - pen_width * 2 - 36
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
        for glow_opacity, offset in [(180, 1), (100, 3), (40, 7)]:
            painter.setPen(QColor(0, 150, 255, glow_opacity))
            painter.drawText(
                self.rect().adjusted(offset, offset, offset, offset),
                Qt.AlignmentFlag.AlignCenter,
                progress_text
            )

        # Main text
        painter.setPen(self._colors['text'])
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, progress_text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Circular Loading Bar")
        self.resize(420, 520)

        self.count = 0
        
        # Set window styles
        # self.setStyleSheet("""
        #     QMainWindow {
        #         background-color: #1a1a2e;
        #     }
        #     QSlider::groove:horizontal {
        #         height: 8px;
        #         background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        #             stop:0 #0066ff, stop:1 #00ccff);
        #         border-radius: 4px;
        #     }
        #     QSlider::handle:horizontal {
        #         width: 18px;
        #         margin: -5px 0;
        #         background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
        #             fx:0.5, fy:0.5, stop:0 #ffffff, stop:1 #aaddff);
        #         border-radius: 9px;
        #     }
        # """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.loading_bar = CircularLoadingBar()
        layout.addWidget(self.loading_bar)

        # self.slider = QSlider(Qt.Orientation.Horizontal)
        # self.slider.setMinimum(0)
        # self.slider.setMaximum(100)
        # self.slider.setValue(0)
        # self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        # self.slider.setTickInterval(10)
        # self.slider.valueChanged.connect(self.loading_bar.setValue)
        # layout.addWidget(self.slider)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

        label = QLabel("Adjust Progress")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #aaddff; 
                font-weight: bold; 
                font-size: 14px;
                padding: 5px;
            }
        """)
        layout.addWidget(label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_progress(self):
        self.count += 1
        self.loading_bar.setValue(self.count)
        if self.count > 100:
            self.count = 0

            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look
    
    # Set application-wide font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())