import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QLabel, QSlider, QVBoxLayout, QWidget

from libs.DatabaseConnector import DatabaseConnector
from libs.GetUser import get_login_user


class ToggleSlider(QSlider):
    """A custom toggle slider with theme switching functionality."""
    
    # Custom signals
    toggled = pyqtSignal(bool)  # Emitted when toggle state changes (True for dark, False for light)
    theme_changed = pyqtSignal(str)  # Emitted with theme name ("dark" or "light")
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        
        # Initialize properties
        self._is_dark_mode: bool = False
        self._database = DatabaseConnector()
        self._animation: QPropertyAnimation = QPropertyAnimation(self, b"value")
        
        # Setup paths
        self._setup_paths()
        
        # Setup UI
        self._setup_ui()
        
        # Load initial theme
        self._load_initial_theme()
        
    def _setup_paths(self) -> None:
        """Setup icon paths using pathlib for better cross-platform compatibility."""
        base_path = Path("C:/Users/O.Feronel/OneDrive - ams OSRAM/Documents/PYTHON/PPM_V5/icon")
        self.sun_icon = str(base_path / "lightMode.png").replace("\\", "/")
        self.moon_icon = str(base_path / "darkMode.png").replace("\\", "/")
        
        # Verify icons exist
        if not Path(self.sun_icon).exists():
            print(f"Warning: Sun icon not found at {self.sun_icon}")
        if not Path(self.moon_icon).exists():
            print(f"Warning: Moon icon not found at {self.moon_icon}")
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        self.setRange(0, 100)
        self.setFixedSize(60, 50)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        # Setup animation
        self._animation.setDuration(600)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _load_initial_theme(self) -> None:
        """Load the initial theme from database."""
        try:
            user = get_login_user()
            user_theme = self._database.get_theme(user)
            
            # Set initial state
            self._is_dark_mode = user_theme == "dark"
            self.setValue(100 if self._is_dark_mode else 0)
            
            # Apply initial style
            self._update_style()
            
        except Exception as e:
            print(f"Error loading theme from database: {e}")
            # Default to light theme on error
            self._is_dark_mode = False
            self.setValue(0)
            self._update_style()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        self.toggle()
        super().mousePressEvent(event)
    
    def toggle(self) -> None:
        """Toggle the slider state."""
        self._is_dark_mode = not self._is_dark_mode
        end_value = 100 if self._is_dark_mode else 0
        
        # Update stylesheet immediately
        self._update_style()
        
        # Animate the handle
        self._animate_to_value(end_value)
        
        # Save theme to database
        self._save_theme_to_db()
        
        # Emit signals
        self.toggled.emit(self._is_dark_mode)
        self.theme_changed.emit("dark" if self._is_dark_mode else "light")
    
    def _animate_to_value(self, end_value: int) -> None:
        """Animate the slider to the specified value."""
        self._animation.stop()
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(end_value)
        self._animation.start()
    
    def _update_style(self) -> None:
        """Update the slider's stylesheet based on current theme."""
        self.setStyleSheet(self._get_style())
    
    def _get_style(self) -> str:
        """Generate the stylesheet based on current theme."""
        groove_base = "#f8ee5c" if not self._is_dark_mode else "#444444"
        border_highlight = "#ff0000" if not self._is_dark_mode else "#4E6366"
        border_shadow = "#F73232" if not self._is_dark_mode else "#008CFF"
        icon_path = self.sun_icon if not self._is_dark_mode else self.moon_icon
        
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
    
    def _save_theme_to_db(self) -> None:
        """Save the current theme to database."""
        try:
            theme = "dark" if self._is_dark_mode else "light"
            user = get_login_user()
            self._database.insert_theme(user, theme)
        except Exception as e:
            print(f"Error saving theme to database: {e}")
    
    # Public methods
    def is_dark_mode(self) -> bool:
        """Return True if dark mode is enabled."""
        return self._is_dark_mode
    
    def set_dark_mode(self, enabled: bool) -> None:
        """Set dark mode state programmatically."""
        if self._is_dark_mode != enabled:
            self.toggle()


class DemoWindow(QWidget):
    """Demo window for testing the ToggleSlider."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Toggle Slider Demo")
        self.setFixedSize(300, 150)
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Create slider
        self.slider = ToggleSlider()
        layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Create label
        self.label = QLabel("Mode: Light")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Connect signals
        self.slider.theme_changed.connect(self._on_theme_changed)
        
    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme change."""
        self.label.setText(f"Mode: {theme.capitalize()}")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application style for better appearance
    app.setStyle('Fusion')
    
    win = DemoWindow()
    win.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()