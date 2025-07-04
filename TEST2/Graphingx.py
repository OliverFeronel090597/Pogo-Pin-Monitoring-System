import sys
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QMenu, QFileDialog, QToolTip
)
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random


class TableGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random Data Line and Bar Chart")
        self.showMaximized()
        self.headers = [
            "ID", "BHW Name", "Date Replaced", "Run Count", "SAP#",
            "Qty. of Pogo Pins Replaced", "Total Price in Euro",
            "Site/s", "Replaced by", "Remarks"
        ]
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.canvas)

        self.plot_random()

    def plot_random(self):
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()  # Right y-axis for price

        num_points = 10
        self.categories = [f"BHW-{random.randint(1000, 9999)}" for _ in range(num_points)]
        self.qty_values = [random.randint(1, 10) for _ in range(num_points)]
        self.price_values = [round(random.uniform(3.0, 50.0), 2) for _ in range(num_points)]

        x = np.arange(len(self.categories))

        # Bar chart for quantity (left y-axis)
        bar_width = 0.4
        bars = ax1.bar(x - bar_width / 2, self.qty_values, width=bar_width, color="steelblue", label="Qty. of Pogo Pins")
        for i, v in enumerate(self.qty_values):
            ax1.text(i - bar_width / 2, v + 0.5, str(v), color='blue', fontsize=8, ha='center')

        # Line chart for price (right y-axis), aligned at top right corner of each bar
        line_x = x + bar_width / 2
        ax2.plot(line_x, self.price_values, color="red", marker="o", label="Total Price in Euro")
        for i, v in enumerate(self.price_values):
            ax2.text(line_x[i], v + 0.5, f"{v:.2f}", color='red', fontsize=8, ha='center')

        ax1.set_ylabel("Qty. of Pogo Pins", color='steelblue')
        ax2.set_ylabel("Total Price in Euro", color='red')

        ax1.set_xticks(x)
        ax1.set_xticklabels(self.categories, rotation=45, ha="right")
        ax1.set_title("Quantity and Price Chart")

        # Enable interactive tooltips via mpl_connect
        self.tooltip_annotation = ax1.annotate("", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
                                               bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        self.tooltip_annotation.set_visible(False)

        def on_motion(event):
            vis = self.tooltip_annotation.get_visible()
            if event.inaxes == ax1:
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        self.tooltip_annotation.xy = (bar.get_x() + bar.get_width() / 2, bar.get_height())
                        text = f"{self.categories[i]}\nQty: {self.qty_values[i]}\nPrice: {self.price_values[i]:.2f}"
                        self.tooltip_annotation.set_text(text)
                        self.tooltip_annotation.set_visible(True)
                        self.canvas.draw_idle()
                        return
            self.tooltip_annotation.set_visible(False)
            self.canvas.draw_idle()

        self.canvas.mpl_connect("motion_notify_event", on_motion)

        self.figure.tight_layout()
        self.canvas.draw()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        save_action = menu.addAction("Save as PNG")
        action = menu.exec(self.canvas.mapToGlobal(pos))
        if action == save_action:
            self.save_plot()

    def save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart As", "chart_output.png", "PNG Files (*.png)")
        if file_path:
            self.figure.savefig(file_path)


if __name__ == "__main__":
    from PyQt6.QtCore import Qt
    app = QApplication(sys.argv)
    win = TableGraphApp()
    win.show()
    sys.exit(app.exec())
