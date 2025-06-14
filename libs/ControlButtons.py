from PyQt6.QtWidgets import QPushButton

class ControlButton(QPushButton):
    def __init__(self, on_click=None, width=150, height=35, name="", parent=None):
        """
        Custom QPushButton with fixed size and optional click action.

        :param on_click: Function to call when the button is clicked.
        :param width: Button width in pixels.
        :param height: Button height in pixels.
        :param name: Text to display on the button.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setText(name)
        self.setProperty("role", "controlButton")

        if on_click is not None:
            self.clicked.connect(on_click)


        self.default_style = """
            QPushButton {
                background-color: #2980b9;
                border: 3px solid #000000;
                border-top-right-radius: 10px;
                padding: 1px;
                
            }
            QPushButton::hover {
                background-color: #70c6ff;
            }
        """
        
        # Highlighted stylesheet
        self.highlighted_style = """
            QPushButton{
                background-color: #2C3E50;
                border: 3px solid #fbff00;
                border-top-right-radius: 10px;
            }
        """

        # Set default style initially
        self.setStyleSheet(self.default_style)

    def highlight(self, highlight=True):
        # Toggle between the default and highlighted styles
        if highlight:
            self.setStyleSheet(self.highlighted_style)
        else:
            self.setStyleSheet(self.default_style)