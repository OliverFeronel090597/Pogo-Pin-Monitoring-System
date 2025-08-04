import numpy as np
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

class RandomWave(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        
        # Create figure and canvas
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Data initialization
        self.categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.bar_data = np.random.randint(10, 100, size=len(self.categories))
        self.line_data = np.random.randint(20, 80, size=len(self.categories))
        self.stats = {
            'mean': np.mean(self.bar_data),
            'median': np.median(self.bar_data),
            'std': np.std(self.bar_data),
            'min': np.min(self.bar_data),
            'max': np.max(self.bar_data)
        }
        
        # Color setup
        self.colors = cm.get_cmap('viridis', len(self.categories))
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(2000)  # Update every 2 seconds
        
        # Initial plot
        self.create_plot()
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def create_plot(self):
        """Create the initial bar and line plot with statistics"""
        self.ax.clear()
        
        # Create bars
        bars = self.ax.bar(
            self.categories, 
            self.bar_data,
            color=self.colors(range(len(self.categories))),
            alpha=0.7,
            label='Values'
        )
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'{height:.0f}',
                ha='center', 
                va='bottom'
            )
        
        # Create line plot
        line, = self.ax.plot(
            self.categories, 
            self.line_data,
            color='red',
            marker='o',
            linestyle='--',
            linewidth=2,
            markersize=8,
            label='Trend'
        )
        
        # Add statistics text
        stats_text = (
            f"Mean: {self.stats['mean']:.1f}\n"
            f"Median: {self.stats['median']:.1f}\n"
            f"Std Dev: {self.stats['std']:.1f}\n"
            f"Min/Max: {self.stats['min']:.0f}/{self.stats['max']:.0f}"
        )
        
        self.ax.text(
            0.02, 0.98,
            stats_text,
            transform=self.ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        # Add title and labels
        self.ax.set_title('Random Statistical Data with Trend Line', pad=20)
        self.ax.set_xlabel('Categories')
        self.ax.set_ylabel('Values')
        self.ax.legend(loc='upper right')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_graph(self):
        """Update the graph with new random data"""
        # Generate new random data with some relation to previous values
        self.bar_data = np.clip(
            self.bar_data + np.random.randint(-15, 15, size=len(self.bar_data)),
            10, 100
        )
        
        # Line data follows bar data but with some variation
        self.line_data = np.clip(
            self.bar_data * 0.8 + np.random.randint(-10, 10, size=len(self.bar_data)),
            20, 80
        )
        
        # Update statistics
        self.stats = {
            'mean': np.mean(self.bar_data),
            'median': np.median(self.bar_data),
            'std': np.std(self.bar_data),
            'min': np.min(self.bar_data),
            'max': np.max(self.bar_data)
        }
        
        # Redraw plot
        self.create_plot()
    
    def stop_animation(self):
        """Stop the animation timer"""
        self.timer.stop()
    
    def start_animation(self, interval=2000):
        """Start the animation timer"""
        self.timer.start(interval)

    def cleanup(self):
        """Clean up resources and stop animations"""
        if hasattr(self, 'timer'):
            if self.timer.isActive():
                self.timer.stop()
            self.timer.deleteLater()
        
        if hasattr(self, 'canvas'):
            self.figure.clf()  # Clear the figure
            self.canvas.close()  # Close the canvas
            del self.figure
            del self.canvas
            del self.ax