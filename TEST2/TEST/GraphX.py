import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 6), tight_layout=True)
        super().__init__(self.fig)
        self.setParent(parent)

        # Create axes
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()
        
        # Configure hover annotation
        self.annot = self.ax1.annotate(
            "", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="black", alpha=0.9),
            arrowprops=dict(arrowstyle="->", color="black"), 
            fontsize=10, ha='center'
        )
        self.annot.set_visible(False)
        
        # Data storage
        self.categories = ["D", "B", "A", "E", "C"]
        self.bar_data = [10, 9, 5, 6, 7]
        self.line_data = [120, 110, 80, 105, 95]
        
        # Connect hover event
        self.cid = self.mpl_connect('motion_notify_event', self.hover_event)
        
        # Initial plot
        self.plot_data()

    def plot_data(self):
        """Plot the bar and line chart with sorted data"""
        self.ax1.clear()
        self.ax2.clear()
        
        # Sort data by bar values
        indices = sorted(range(len(self.bar_data)), key=lambda i: self.bar_data[i])
        self.sorted_cats = [self.categories[i] for i in indices]
        self.sorted_bars = [self.bar_data[i] for i in indices]
        self.sorted_lines = [self.line_data[i] for i in indices]
        x = np.arange(len(self.sorted_cats))
        
        # Plot bars
        self.bar_rects = self.ax1.bar(
            x, self.sorted_bars, 
            color='tomato', alpha=0.7,
            width=0.6, edgecolor='darkred', linewidth=1
        )
        
        # Add bar value labels
        for i, (rect, val) in enumerate(zip(self.bar_rects, self.sorted_bars)):
            height = rect.get_height()
            self.ax1.text(
                rect.get_x() + rect.get_width()/2., height + 0.3,
                f'{val}', ha='center', va='bottom', 
                fontsize=9, color='darkred'
            )
        
        # Plot line with markers
        self.line_plot, = self.ax2.plot(
            x, self.sorted_lines, 
            color='dodgerblue', marker='o', 
            markersize=8, linewidth=2, 
            markeredgecolor='navy', markerfacecolor='skyblue'
        )
        
        # Add line value labels
        for i, val in enumerate(self.sorted_lines):
            self.ax2.text(
                x[i], val + 3, f'{val}', 
                ha='center', va='bottom', 
                fontsize=9, color='navy'
            )
        
        # Configure axes
        self.ax1.set_ylabel("Bar Values", color='darkred', fontsize=10)
        self.ax1.set_ylim(0, max(self.sorted_bars) + 2)
        self.ax1.tick_params(axis='y', labelcolor='darkred')
        
        self.ax2.set_ylabel("Line Values", color='navy', fontsize=10)
        self.ax2.set_ylim(0, max(self.sorted_lines) + 15)
        self.ax2.tick_params(axis='y', labelcolor='navy')
        
        # X-axis configuration
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(self.sorted_cats, fontsize=10, rotation=45, ha='right')
        self.ax1.set_xlim(-0.5, len(x)-0.5)
        
        # Title and grid
        self.ax1.set_title(
            "Interactive Bar-Line Chart with Hover Tooltips", 
            fontsize=12, fontweight='bold', pad=20
        )
        self.ax1.grid(True, linestyle=':', alpha=0.4)
        
        # Create legend
        bar_legend = Rectangle((0,0), 1, 1, fc='tomato', alpha=0.7, edgecolor='darkred')
        line_legend = Rectangle((0,0), 1, 1, fc='dodgerblue', alpha=0.7, edgecolor='navy')
        self.ax1.legend(
            [bar_legend, line_legend], ['Bar Values', 'Line Values'],
            loc='upper left', fontsize=9
        )
        
        # Store data for hover events
        self.sorted_data = list(zip(self.sorted_cats, self.sorted_bars, self.sorted_lines))
        
        self.draw()

    def hover_event(self, event):
        """Handle mouse hover events to show tooltips"""
        if event.inaxes == self.ax1:
            # Check bars
            for i, rect in enumerate(self.bar_rects):
                if rect.contains(event)[0]:
                    cat, bar_val, line_val = self.sorted_data[i]
                    self.show_annotation(rect, f"Category: {cat}\nBar: {bar_val}\nLine: {line_val}")
                    return
            
            # Check line points
            xdata, ydata = self.line_plot.get_data()
            for i, (x, y) in enumerate(zip(xdata, ydata)):
                if abs(event.xdata - x) < 0.3 and abs(event.ydata - y) < 5:
                    cat, bar_val, line_val = self.sorted_data[i]
                    self.show_annotation(None, f"Category: {cat}\nBar: {bar_val}\nLine: {line_val}", (x, y))
                    return
        
        self.hide_annotation()

    def show_annotation(self, rect, text, xy=None):
        """Show annotation at specified position"""
        if xy is None and rect:
            xy = (rect.get_x() + rect.get_width()/2, rect.get_height())
        
        self.annot.xy = xy
        self.annot.set_text(text)
        self.annot.set_visible(True)
        
        # Adjust position if near edges
        x, y = self.annot.xy
        x_offset = -40 if x > (len(self.sorted_cats) * 0.7) else 20
        y_offset = -40 if y > (max(self.sorted_bars) * 0.7) else 20
        self.annot.xyann = (x_offset, y_offset)
        
        self.draw()

    def hide_annotation(self):
        """Hide the annotation"""
        if self.annot.get_visible():
            self.annot.set_visible(False)
            self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Bar-Line Chart")
        self.resize(1000, 700)
        
        self.canvas = GraphCanvas()
        button = QPushButton("Refresh Chart")
        button.setStyleSheet("font-size: 12px; padding: 5px;")
        button.clicked.connect(self.canvas.plot_data)
        
        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.canvas)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())