from PyQt6.QtWidgets import QDialog, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


class NumberInputDialog(QDialog):
    def __init__(self, initial_sites="", parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Sites")
        self.setWindowIcon(QIcon(":/mainlogo.png"))
        self.setFixedSize(450, 250)

        self.selected_numbers = self.parse_initial_sites(initial_sites)
        self.buttons = {}

        # Layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QGridLayout()
        self.control_layout = QHBoxLayout()

        # Site button styling
        self.button_size = QSize(70, 30)
        self.site_style_selected = """
            QPushButton {
                background-color: #fd5000;
                color: white;
                border: 2px solid #2C3E50;
                border-radius: 4px;
            }
        """
        self.site_style_deselected = """
            QPushButton {
                background-color: lightgray;
                color: black;
                border: 2px solid gray;
                border-radius: 4px;
            }
        """

        # Create 36 site buttons (6x6 grid)
        for i in range(1, 37):  # 1 to 36
            button = QPushButton(str(i))
            button.setFixedSize(self.button_size)
            button.clicked.connect(lambda _, num=i: self.toggle_number(num))
            row, col = divmod(i - 1, 6)
            self.button_layout.addWidget(button, row, col)
            self.buttons[i] = button

        # Control Buttons
        self.select_all_button = self.create_control_button("Select All", self.select_all)
        self.deselect_all_button = self.create_control_button("Deselect All", self.deselect_all)
        self.select_16_button = self.create_control_button("16 Sites", self.select_16_sites)
        self.ok_button = self.create_control_button("OK", self.accept)

        self.control_layout.addWidget(self.deselect_all_button)
        self.control_layout.addWidget(self.select_all_button)
        self.control_layout.addWidget(self.select_16_button)
        self.control_layout.addWidget(self.ok_button)

        # Add layouts to main layout
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.control_layout)

        self.setLayout(self.main_layout)
        self.update_button_color()

    def create_control_button(self, text, slot):
        button = QPushButton(text)
        button.setFixedSize(100, 30)
        button.clicked.connect(slot)
        button.setStyleSheet("""
            QPushButton {
                background-color: #4682B4;
                color: white;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #5A9BD5;
            }
        """)
        return button

    def parse_initial_sites(self, initial_sites):
        if "36 sites" in initial_sites:
            return set(range(1, 37))
        elif "16 sites" in initial_sites:
            return set(range(1, 17))
        else:
            return {int(num) for num in initial_sites.split(", ") if num.isdigit()}

    def toggle_number(self, number):
        if number in self.selected_numbers:
            self.selected_numbers.remove(number)
        else:
            self.selected_numbers.add(number)
        self.update_button_color()

    def update_button_color(self):
        for num, button in self.buttons.items():
            if num in self.selected_numbers:
                button.setStyleSheet(self.site_style_selected)
            else:
                button.setStyleSheet(self.site_style_deselected)

    def select_all(self):
        self.selected_numbers = set(self.buttons.keys())
        self.update_button_color()

    def deselect_all(self):
        self.selected_numbers.clear()
        self.update_button_color()

    def select_16_sites(self):
        self.selected_numbers = set(range(1, 17))
        self.update_button_color()

    def accept(self):
        self.selected_numbers = sorted(self.selected_numbers)
        super().accept()
