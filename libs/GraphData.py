import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QMenu
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class GraphData(QWidget):
    def __init__(self, categories, bar_data, line_data, right_label, left_label, 
                 top_label, bottom_label, parent=None):
        super().__init__(parent)
        self._init_ui(categories, bar_data, line_data, right_label, 
                     left_label, top_label, bottom_label)

    def _init_ui(self, categories, bar_data, line_data, right_label, 
                left_label, top_label, bottom_label):
        """Initialize the UI components."""
        self.setWindowTitle("Bar and Line Graph Example")
        
        # Store labels for later use
        self.labels = {
            'right': right_label,
            'left': left_label,
            'top': top_label,
            'bottom': bottom_label
        }
        
        # Create layout and figure
        layout = QVBoxLayout(self)
        self.figure, self.ax1 = plt.subplots(figsize=(12, 9))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Process and plot data
        sorted_categories, sorted_bar_data, sorted_line_data = self._process_data(categories, bar_data, line_data)
        self._create_bar_chart(sorted_categories, sorted_bar_data)
        self._create_line_chart(sorted_categories, sorted_line_data)
        
        # Final adjustments
        self._adjust_layout()
        self.canvas.draw()

    def _process_data(self, categories, bar_data, line_data):
        """Process and sort input data."""
        bar_data = np.asarray(bar_data, dtype=float)
        line_data = np.asarray(line_data, dtype=float)
        sorted_indices = np.argsort(bar_data)[::-1]
        return (
            np.array(categories)[sorted_indices],
            bar_data[sorted_indices],
            line_data[sorted_indices]
        )

    def _create_bar_chart(self, categories, bar_data):
        """Create the bar chart component."""
        bar_width = 0.6
        self.x_positions = np.arange(len(categories))
        
        self.bars = self.ax1.bar(
            self.x_positions - bar_width / 2, 
            bar_data, 
            bar_width, 
            color='blue', 
            alpha=0.6, 
            label='Bar Data'
        )
        
        self.ax1.set_ylabel(self.labels['left'])
        self.ax1.set_title(self.labels['top'])
        self.ax1.set_xticks(self.x_positions)
        self.ax1.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)
        
        # Add bar labels
        for bar in self.bars:
            height = bar.get_height()
            self.ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                color=bar.get_facecolor()
            )

    def _create_line_chart(self, categories, line_data):
        """Create the line chart component."""
        self.ax2 = self.ax1.twinx()
        self.line_plot, = self.ax2.plot(
            self.x_positions, 
            line_data, 
            color='red', 
            marker='o', 
            label='Total Price in EURO'
        )
        self.ax2.set_ylabel(self.labels['right'])
        
        # Add line point labels
        for i, value in enumerate(line_data):
            self.ax2.text(
                self.x_positions[i], 
                value, 
                f'{value:.2f}', 
                color=self.line_plot.get_color(), 
                ha='center', 
                va='bottom'
            )
        
        # Add legend with click functionality
        self._setup_legend()

    def _setup_legend(self):
        """Configure the legend with click functionality."""
        lines, labels = self.ax1.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        legend = self.ax1.legend(
            lines + [self.line_plot], 
            labels + labels2, 
            loc='upper right'
        )
        
        # Connect legend click event
        for legend_text in legend.get_texts():
            legend_text.set_picker(True)
            legend_text.figure.canvas.mpl_connect(
                'pick_event', 
                lambda event: self._on_legend_click(event, legend)
            )

    def _on_legend_click(self, event, legend):
        """Handle legend click events."""
        legend_item = event.artist
        is_visible = not legend_item.get_visible()
        legend_item.set_visible(is_visible)
        
        index = legend.get_texts().index(legend_item)
        if index < len(self.bars):
            for bar in self.bars:
                bar.set_visible(is_visible)
        else:
            self.line_plot.set_visible(is_visible)
        
        self.canvas.draw()

    def _adjust_layout(self):
        """Adjust the layout and add bottom label."""
        max_bar_value = max(self.ax1.get_ylim()[1], 0)
        padding = 0.05 * max_bar_value
        self.ax1.set_ylim(0, max_bar_value + padding)
        
        self.figure.subplots_adjust(
            left=0.03, 
            right=0.97, 
            top=0.92, 
            bottom=0.15
        )
        
        # Add bottom label
        self.ax1.text(
            0.5, -0.18,  # Adjusted position
            self.labels['bottom'], 
            transform=self.ax1.transAxes, 
            ha='center', 
            va='center', 
            fontsize=12, 
            color='black',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )
        
        self.figure.tight_layout(pad=0.5)

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # Example data
#     categories = ['Category A', 'Category B', 'Category C']
#     bar_data = [10, 20, 15]
#     line_data = [5, 10, 7]
#     right_label = 'Total Price in EURO'
#     left_label = 'Quantity'
#     top_label = 'Bar and Line Chart'
#     bottom_label = 'This is a label under the plot'

#     window = GraphData(categories, bar_data, line_data, right_label, 
#                       left_label, top_label, bottom_label)
#     window.show()
#     sys.exit(app.exec())