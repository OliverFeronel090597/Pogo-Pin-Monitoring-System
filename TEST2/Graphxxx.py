import sys
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QMainWindow, QPushButton, QScrollArea, QTabWidget,
                             QVBoxLayout, QWidget)

# Sample data
data = """
ID,	BHW Name,	Date Replaced,	Run Count,	SAP#	,Qty. of Pogo Pins Replaced,	Total Price in Euro,	Site/s,	Replaced by	Remarks
7390,18621-LB03-A0-001,2025-07-28,94934,10009442,5,15.3,1, 2,ACAO,Replaced pogo pins on site 1 & site 2, Pin# 7,1,2,9 & 10 verified by TPE-MTAN.
7389,19210-LB01-B0-001,2025-07-27,236142,10009442,2,6.12,4,VBAD,Replaced data log failure pins 4 and 9; Swapped Site 4 and 2.
7388,19210-LB01-B0-001,2025-07-27,235624,10009442,5,15.3,4,VBAD,Failure transfer- replaced pins 2, 8, 12, 14, 16 on Site 4.
7387,TOWER_33,2025-07-27,37669332,10009981,1,3.85,12,H.CEZAR,repaced 1 suken pogo pin on module 12
7386,51491-DW04-C0-013,2025-07-25,940743,10025462,288,768.96,16 sites,DPUM,replaced 288 pins due to small tip diameter, OS failed. RC: 940,743
7385,18621-LB03-A1-003,2025-07-25,57833,10009442,3,9.18,2,M.OLIGARIO,replaced sunken pogopins site2 3pcs
7384,50295-LB02-A0-019,2025-07-24,1982124,10025462,30,80.1,2, 12, 13, 14, 16,ACAO,Replaced pogo pins on site 2,12,13,14, & 16 (C3 C4 D3 D4).
7383,50295-LB02-A0-019,2025-07-24,1982124,10025462,30,80.1,2, 12, 13, 14, 16,ACAO,Replaced pogo pins on site 2,12,13,14, & 16 (C3 C4 D3 D4).
7382,18519-DW01-B0-002,2025-07-23,4257091,10012962,60,184.8,1, 2, 3, 4,ACAO,Replaced all pogo pins due to high runcount.
7381,50295-LB02-A0-020,2025-07-23,1877885,10025462,16,42.72,6, 8, 12, 14,VBAD,Replaced C3,C4,D3,D4 on Site 6, 8, 12, 14.
7380,18036-LB01-A1-001,2025-07-23,133679,10009442,1,3.06,1,VBAD,Replaced 1pc sunken pin before confirming to storage.
7379,18036-LB01-A0-002,2025-07-23,30013,10009442,4,12.24,1,VBAD,Replaced 24-27 as per TPE request- datalog failure.
7378,50373-LB02-B0-001,2025-07-22,368144,10032704,1,3.74,4,M.OLIGARIO,replaced broken pogopins site4 pin # 8 1pc1
7377,50373-LB02-B0-001,2025-07-22,367935,10032704,2,7.48,4,M.OLIGARIO,replaced broken pogopins site4 pin # 8 
7376,18085-LB04-A0-002,2025-07-22,29905,10009442,4,12.24,2,VBAD,Replaced pin 5, 6, 27, 28 on Site 2 as per tpe nneq request.
7375,18621-LB03-A1-001,2025-07-22,56760,10009442,5,15.3,1,VBAD,Replaced 5pcs bent pins on Site 1.
7374,18621-LB03-A1-001,2025-07-22,56698,10009442,1,3.06,1,ACAO,Replaced stuckup pin#5 on site 1.
7373,50122-LB01-A1-004,2025-07-22,250,10009442,88,269.28,1, 2, 3, 4,ACAO,Replaced all pogo pins as per request by TPE-MTAN (runcount: 459,251) 88pcs pogo pins.
7372,51491-DW04-C0-016,2025-07-21,18,10025462,1,2.67,12,DPUM,replaced pin name SDA at site 12, OS failed
7371,51491-DW04-C0-012,2025-07-21,855,10025462,288,768.96,16 sites,DPUM,replaced all pins (small tip diameter) 
7370,18621-LB03-A0-002,2025-07-21,91466,10009442,4,12.24,1, 2,VBAD,Replace pogopin site 1 pin# 3 & 9/ site 2 pin 2& 16.
7369,50295-LB02-A0-014,2025-07-21,1242480,10025462,4,10.68,11,VBAD,Replaced C3, C4, D3, D4 on Site 11.
7368,18621-LB03-A1-003,2025-07-21,1091615,10009442,16,48.96,2,VBAD,Replaced all pins on inserposer socket on Site 2. (16pcs)
7367,18621-LB03-A1-001,2025-07-21,55925,10009442,3,9.18,1, 2,VBAD,Replaced 2pcs on Site 1; 1pc on Siite 1.
"""

class DataAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pogo Pin Replacement Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load and prepare data
        self.df = pd.read_csv(StringIO(data), parse_dates=['Date Replaced'])
        # Convert SAP# to string to prevent scientific notation
        self.df['SAP#'] = self.df['SAP#'].astype(str)
        # Drop ID and Remarks columns
        self.df = self.df.drop(columns=['ID', 'Remarks'])
        
        self.df['Run Count'] = self.df['Run Count'].astype(int)
        self.df['Qty. of Pogo Pins Replaced'] = self.df['Qty. of Pogo Pins Replaced'].astype(int)
        self.df['Total Price in Euro'] = self.df['Total Price in Euro'].astype(float)
        
        # Extract sites information
        self.df['Site Count'] = self.df['Site/s'].apply(lambda x: len(str(x).split(',')) if 'sites' not in str(x) else int(str(x).split()[0]))
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Create controls
        self.create_controls()
        
        # Create tab widget for plots
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Generate initial plots
        self.update_plots()
        
    def create_controls(self):
        control_layout = QHBoxLayout()
        
        # Graph type selector
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems([
            "Line Chart",
            "Bar Chart",
            "Histogram",
            "Box Plot",
            "Pie Chart",
            "Violin Plot",
            "Heatmap",
            "Pair Plot"
        ])
        control_layout.addWidget(QLabel("Graph Type:"))
        control_layout.addWidget(self.graph_type_combo)
        
        # X-axis selector
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItems(self.df.select_dtypes(include=['number', 'datetime', 'object']).columns)
        control_layout.addWidget(QLabel("X-Axis:"))
        control_layout.addWidget(self.x_axis_combo)
        
        # Y-axis selector
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItems(self.df.select_dtypes(include=['number']).columns)
        control_layout.addWidget(QLabel("Y-Axis:"))
        control_layout.addWidget(self.y_axis_combo)
        
        # Color by selector
        self.color_combo = QComboBox()
        self.color_combo.addItems(['None'] + list(self.df.select_dtypes(include=['object']).columns))
        control_layout.addWidget(QLabel("Color By:"))
        control_layout.addWidget(self.color_combo)
        
        # Update button
        self.update_btn = QPushButton("Update Plots")
        self.update_btn.clicked.connect(self.update_plots)
        control_layout.addWidget(self.update_btn)
        
        # Analysis button
        self.analysis_btn = QPushButton("Run Analysis")
        self.analysis_btn.clicked.connect(self.run_analysis)
        control_layout.addWidget(self.analysis_btn)
        
        self.layout.addLayout(control_layout)
    
    def update_plots(self):
        self.tab_widget.clear()
        
        # Get selected options
        graph_type = self.graph_type_combo.currentText()
        x_axis = self.x_axis_combo.currentText()
        y_axis = self.y_axis_combo.currentText()
        color_by = self.color_combo.currentText() if self.color_combo.currentText() != 'None' else None
        
        # Create standard plots
        self.create_plot_tab("Date vs Total Price", self.create_line_plot, 
                            'Date Replaced', 'Total Price in Euro')
        
        self.create_plot_tab("Pins Replaced per BHW", self.create_bar_plot, 
                            'Qty. of Pogo Pins Replaced', 'BHW Name', sort=True)
        
        self.create_plot_tab("Cost by Engineer", self.create_bar_plot_sum, 
                            'Total Price in Euro', 'Replaced by')
        
        # Create custom plot based on user selection
        if graph_type == "Line Chart":
            self.create_plot_tab(f"Custom Line: {x_axis} vs {y_axis}", 
                                self.create_line_plot, x_axis, y_axis)
        elif graph_type == "Bar Chart":
            self.create_plot_tab(f"Custom Bar: {x_axis} by {y_axis}", 
                                self.create_bar_plot, x_axis, y_axis, sort=True)
        elif graph_type == "Histogram":
            self.create_plot_tab(f"Histogram: {x_axis}", 
                                self.create_histogram, x_axis)
        elif graph_type == "Box Plot":
            self.create_plot_tab(f"Box Plot: {y_axis} by {x_axis}", 
                                self.create_box_plot, x_axis, y_axis)
        elif graph_type == "Pie Chart":
            self.create_plot_tab(f"Pie Chart: {x_axis}", 
                                self.create_pie_chart, x_axis)
        elif graph_type == "Violin Plot":
            self.create_plot_tab(f"Violin Plot: {y_axis} by {x_axis}", 
                                self.create_violin_plot, x_axis, y_axis)
        elif graph_type == "Heatmap":
            self.create_plot_tab("Correlation Heatmap", 
                                self.create_heatmap)
        elif graph_type == "Pair Plot":
            self.create_plot_tab("Pair Plot", 
                                self.create_pair_plot)
    
    def create_plot_tab(self, title, plot_func, *args, **kwargs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area for plots that might be large
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Create figure
        fig = Figure(figsize=(10, 6), dpi=100)
        canvas = FigureCanvas(fig)
        
        # Call the plotting function
        plot_func(fig, *args, **kwargs)
        
        canvas.draw()
        scroll.setWidget(canvas)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, title)
    
    def create_line_plot(self, fig, x_col, y_col):
        ax = fig.add_subplot(111)
        sns.lineplot(data=self.df, x=x_col, y=y_col, marker='o', ax=ax)
        ax.set_title(f"{x_col} vs {y_col}")
        ax.grid(True)
        plt.setp(ax.get_xticklabels(), rotation=45)
    
    def create_bar_plot(self, fig, x_col, y_col, sort=False):
        ax = fig.add_subplot(111)
        data = self.df.sort_values(by=x_col, ascending=False) if sort else self.df
        sns.barplot(data=data, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"{x_col} by {y_col}")
        ax.grid(True)
    
    def create_bar_plot_sum(self, fig, x_col, y_col):
        ax = fig.add_subplot(111)
        grouped = self.df.groupby(y_col)[x_col].sum().reset_index()
        sns.barplot(data=grouped, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"Total {x_col} by {y_col}")
        ax.grid(True)
    
    def create_histogram(self, fig, col):
        ax = fig.add_subplot(111)
        sns.histplot(data=self.df, x=col, kde=True, ax=ax)
        ax.set_title(f"Distribution of {col}")
        ax.grid(True)
    
    def create_box_plot(self, fig, x_col, y_col):
        ax = fig.add_subplot(111)
        sns.boxplot(data=self.df, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"Distribution of {y_col} by {x_col}")
        ax.grid(True)
        plt.setp(ax.get_xticklabels(), rotation=45)
    
    def create_pie_chart(self, fig, col):
        ax = fig.add_subplot(111)
        counts = self.df[col].value_counts()
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title(f"Proportion of {col}")
        ax.axis('equal')
    
    def create_violin_plot(self, fig, x_col, y_col):
        ax = fig.add_subplot(111)
        sns.violinplot(data=self.df, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"Distribution of {y_col} by {x_col}")
        ax.grid(True)
        plt.setp(ax.get_xticklabels(), rotation=45)
    
    def create_heatmap(self, fig):
        ax = fig.add_subplot(111)
        numeric_df = self.df.select_dtypes(include=['number'])
        sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax)
        ax.set_title("Correlation Heatmap")
    
    def create_pair_plot(self, fig):
        # Pair plot is special - we need to create a separate figure
        pair_fig = sns.pairplot(self.df.select_dtypes(include=['number'])).fig
        fig.clf()
        fig = pair_fig
        fig.suptitle("Pair Plot of Numerical Variables", y=1.02)
    
    def run_analysis(self):
        analysis_tab = QWidget()
        layout = QVBoxLayout(analysis_tab)
        
        # Basic statistics
        stats_label = QLabel("<h2>Basic Statistics</h2>")
        layout.addWidget(stats_label)
        
        # Format numeric stats to 2 decimal places without scientific notation
        numeric_stats = self.df.describe().apply(lambda x: round(x, 2)).to_html()
        stats_text = QLabel(numeric_stats)
        stats_text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(stats_text)
        
        # Cost analysis
        cost_label = QLabel("<h2>Cost Analysis</h2>")
        layout.addWidget(cost_label)
        
        total_cost = self.df['Total Price in Euro'].sum()
        avg_cost_per_pin = total_cost / self.df['Qty. of Pogo Pins Replaced'].sum()
        cost_text = QLabel(f"""
            <p>Total Replacement Cost: €{total_cost:,.2f}</p>
            <p>Average Cost per Pin: €{avg_cost_per_pin:,.2f}</p>
            <p>Most Expensive Replacement: €{self.df['Total Price in Euro'].max():,.2f}</p>
            <p>Least Expensive Replacement: €{self.df['Total Price in Euro'].min():,.2f}</p>
        """)
        cost_text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(cost_text)
        
        # Engineer analysis
        engineer_label = QLabel("<h2>Engineer Analysis</h2>")
        layout.addWidget(engineer_label)
        
        engineer_stats = self.df.groupby('Replaced by').agg({
            'Qty. of Pogo Pins Replaced': 'sum',
            'Total Price in Euro': lambda x: round(x.sum(), 2),  # Format to 2 decimal places
            'BHW Name': 'count'
        }).rename(columns={'BHW Name': 'Repair Count'}).to_html(float_format=lambda x: f"{x:,.2f}")
        engineer_text = QLabel(engineer_stats)
        engineer_text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(engineer_text)
        
        # BHW analysis
        bhw_label = QLabel("<h2>BHW Analysis</h2>")
        layout.addWidget(bhw_label)
        
        bhw_stats = self.df.groupby('BHW Name').agg({
            'Qty. of Pogo Pins Replaced': 'sum',
            'Total Price in Euro': lambda x: round(x.sum(), 2),  # Format to 2 decimal places
            'Replaced by': 'count'
        }).rename(columns={'Replaced by': 'Repair Count'}).to_html(float_format=lambda x: f"{x:,.2f}")
        bhw_text = QLabel(bhw_stats)
        bhw_text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(bhw_text)
        
        # Add scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(analysis_tab)
        
        # Add as a new tab
        self.tab_widget.addTab(scroll, "Analysis Results")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataAnalyzer()
    window.show()
    sys.exit(app.exec())