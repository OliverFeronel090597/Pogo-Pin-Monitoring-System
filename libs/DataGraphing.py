from io import BytesIO

from PyQt6.QtCore import QObject, QSize, Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QClipboard, QImage
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMenu,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from libs.CalendarLineEdit import DateRangeLineEdit
from libs.CustomComboBox import CustomDropdown
from libs.CustomSpinBox import CustomSpinBox
from libs.DatabaseConnector import DatabaseConnector
from libs.GraphData import GraphData


class GraphWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, func, start_date, end_date, selected_sap, database):
        super().__init__()
        self.func = func
        self.start_date = start_date
        self.end_date = end_date
        self.selected_sap = selected_sap
        self.database = database

    def run(self):
        try:
            result = {
                "categories": [],
                "bar_data": [],
                "line_data": [],
                "left_label": "",
                "right_label": "",
                "top_label": "",
                "bottom_label": ""
            }

            if self.func == "BHW Serial":
                data = self.database.graph_by_bhw(self.start_date, self.end_date)
                # Collect data first
                temp_data = []
                for lb, sap, qty in data:
                    price_data = self.database.get_sap_price(sap)
                    price = price_data[0] if price_data and price_data[0] is not None else 0
                    try:
                        total = float(qty) * float(price)
                    except ValueError:
                        total = 0
                    temp_data.append((lb, int(qty), total))
                
                # Sort by bar_data (qty) in descending order
                temp_data.sort(key=lambda x: x[1], reverse=True)
                
                # Populate result
                for lb, qty, total in temp_data:
                    result["categories"].append(lb)
                    result["bar_data"].append(qty)
                    result["line_data"].append(f"{total:.2f}")

                result["left_label"] = "Pogo Pin Qty."
                result["right_label"] = "Total Price in Euro"
                result["top_label"] = f"BHW Pogo Pin Quantity and Price from {self.start_date} to {self.end_date}"
                result["bottom_label"] = "BHW Serial"

            elif self.func == "SAP Number":
                data = self.database.get_sap_use(self.start_date, self.end_date)
                unique_saps = list({sap for (sap,) in data})
                
                # Collect data first
                temp_data = []
                for sap in unique_saps:
                    price_data = self.database.get_sap_price(sap)
                    qty = self.database.get_total_pogo_use(self.start_date, self.end_date, sap)
                    price = price_data[0] if price_data and price_data[0] is not None else 0
                    if qty is None:
                        continue
                    try:
                        total = float(price) * float(qty)
                    except ValueError:
                        total = 0
                    temp_data.append((sap, int(qty), total))
                
                # Sort by bar_data (qty) in descending order
                temp_data.sort(key=lambda x: x[1], reverse=True)
                
                # Populate result
                for sap, qty, total in temp_data:
                    result["categories"].append(sap)
                    result["bar_data"].append(qty)
                    result["line_data"].append(f"{total:.2f}")

                result["left_label"] = "Pogo Pin Qty."
                result["right_label"] = "Total Price in Euro"
                result["top_label"] = f"SAP Number Pogo Pin Quantity and Price from {self.start_date} to {self.end_date}"
                result["bottom_label"] = "SAP Number"

            elif self.func == "SAP Contributor":
                data = self.database.get_lb_use_sap(self.start_date, self.end_date, self.selected_sap)
                if data:
                    # Collect data first
                    temp_data = []
                    for lb in data:
                        pogo_use = self.database.get_lb_total_use(self.start_date, self.end_date, lb)
                        price = self.database.get_sap_price(self.selected_sap)[0]
                        if price is None or pogo_use is None:
                            continue
                        try:
                            total_price = float(pogo_use) * float(price)
                        except ValueError:
                            total_price = 0
                        temp_data.append((lb, int(pogo_use), total_price))
                    
                    # Sort by bar_data (pogo_use) in descending order
                    temp_data.sort(key=lambda x: x[1], reverse=True)
                    
                    # Populate result
                    for lb, pogo_use, total_price in temp_data:
                        result["categories"].append(lb)
                        result["bar_data"].append(pogo_use)
                        result["line_data"].append("{:.2f}".format(total_price))

                    result["left_label"] = "Pogo Pin Qty."
                    result["right_label"] = "Total Price in Euro"
                    result["top_label"] = f"SAP no. {self.selected_sap} used in different loadboards from {self.start_date} to {self.end_date}"
                    result["bottom_label"] = "SAP Contributor"

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class DataGraphing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database = DatabaseConnector()
        self.current_graph_widget = None
        self.main_parent = parent
        self.setObjectName("dataGraphingWidget")
        self.init_ui()
        self.apply_styles()
        
        # Load sample data on start
        QApplication.processEvents()  # Ensure UI is fully loaded
        QTimer.singleShot(100, self.load_sample_data)

    def apply_styles(self):
        """Apply styles directly to the widget using widget type selectors"""
        self.setStyleSheet("""
            /* ##############################################################################
               #####                           Data Graph                               #####
               ############################################################################## */

            QWidget[role="graphContainer"] {
                background-color: #FFFFFF;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }

            QWidget[role="controlsWidget"] {
                background-color: transparent;
                padding: 1px;
            }

            QLabel[role="dataGraph"] {
                font-size: 12px;
                font-weight: bold;
                color: #34495e;
                background-color: transparent;
            }

            /* Generic input styling */
            QLineEdit[role="dataGraph"] {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                padding: 1px;
                border-radius: 4px;
                font-size: 11pt;
            }

            QLineEdit[role="dataGraph"]:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }

            /* ComboBox base styling */
            QComboBox[role="dataGraph"] {
                background-color: #ffffff;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                padding: 1px;
                font-size: 11pt;
                border-radius: 4px;
            }

            QComboBox[role="dataGraph"]:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }

            /* ComboBox dropdown list */
            QComboBox[role="dataGraph"] QAbstractItemView {
                background-color: #ffffff;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                font-size: 11pt;
                font-family: 'Segoe UI', sans-serif;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                outline: none;
            }

            QComboBox[role="dataGraph"] QAbstractItemView::item:hover {
                background-color: #D6EAF8;
                color: #2C3E50;
            }

            /* ComboBox scrollbar */
            QComboBox[role="dataGraph"] QScrollBar:vertical {
                border: none;
                background: #ECF0F1;
                width: 10px;
                margin: 2px 0;
                border-radius: 5px;
            }

            QComboBox[role="dataGraph"] QScrollBar::handle:vertical {
                background: #95A5A6;
                border-radius: 5px;
            }

            QComboBox[role="dataGraph"] QScrollBar::handle:vertical:hover {
                background: #7F8C8D;
            }

            QComboBox[role="dataGraph"] QScrollBar::add-line:vertical,
            QComboBox[role="dataGraph"] QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QComboBox[role="dataGraph"] QScrollBar::add-page:vertical,
            QComboBox[role="dataGraph"] QScrollBar::sub-page:vertical {
                background: none;
            }

            /* Hide drop-down button and arrow */
            QComboBox[role="dataGraph"]::drop-down {
                width: 0px;
                border: none;
            }

            QComboBox[role="dataGraph"]::down-arrow {
                width: 0px;
                height: 0px;
                image: none;
            }

            /* Generate Button */
            QPushButton[role="dataGraph"] {
                background-color: #3498DB;
                border: 1px solid #2980B9;
                color: white;
                border-radius: 4px;
                padding: 1px;
                font-size: 11pt;
                font-weight: bold;
            }

            QPushButton[role="dataGraph"]:hover {
                background-color: #2980B9;
            }

            QPushButton[role="dataGraph"]:pressed {
                background-color: #1F618D;
            }

            QPushButton[role="dataGraph"]:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }

            /* SpinBox styling */
            QSpinBox[role="graphLimit"] {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-size: 11pt;
                padding: 1px;
                selection-background-color: #D6EAF8;
                selection-color: #2C3E50;
            }

            QSpinBox[role="graphLimit"]:focus {
                border: 1px solid #3498db;
            }

            /* Hide SpinBox up/down buttons */
            QSpinBox[role="graphLimit"]::up-button,
            QSpinBox[role="graphLimit"]::down-button {
                width: 0px;
                height: 0px;
                border: none;
                background: none;
            }

            /* Context Menu */
            QMenu#graphContextMenu {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #3498DB;
                border-radius: 4px;
                padding: 1px;
            }

            QMenu#graphContextMenu::item {
                padding: 1px;
                background-color: transparent;
            }

            QMenu#graphContextMenu::item:selected {
                background-color: #3498DB;
                color: white;
            }

            /* Calendar Line Edit in Data Graph */
            QLineEdit#dataRangeLineEdit {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                padding: 1px;
                border-radius: 4px;
                font-size: 11pt;
            }

            QLineEdit#dataRangeLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }

            /* CustomSpinBox specific */
            QSpinBox#graphLimitSpinBox {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-size: 11pt;
                padding: 1px;
                selection-background-color: #D6EAF8;
                selection-color: #2C3E50;
            }

            QSpinBox#graphLimitSpinBox:focus {
                border: 1px solid #3498db;
            }

            QSpinBox#graphLimitSpinBox::up-button,
            QSpinBox#graphLimitSpinBox::down-button {
                width: 0px;
                height: 0px;
                border: none;
                background: none;
            }

            /* Main widget background */
            QWidget#dataGraphingWidget {
                background-color: #F5F6F7;
            }
            /* Base Tooltip - using monospace for alignment */
            QToolTip {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #3498DB;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: 'Courier New', 'Consolas', 'Segoe UI', monospace;
                font-size: 10pt;
                font-weight: 400;
                opacity: 240;
                letter-spacing: 0.3px;
                word-spacing: 0.5px;
            }

        """)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Create a container widget for the graph area
        self.graph_container = QWidget()
        self.graph_container.setObjectName("graphContainer")
        self.graph_container.setProperty("role", "graphContainer")
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add a placeholder label when no graph is shown
        self.placeholder_label = QLabel("📊 Generate a graph to see data visualization")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #95a5a6;
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        self.graph_layout.addWidget(self.placeholder_label)
        
        main_layout.addWidget(self.graph_container, stretch=1)

        # Controls container
        controls_widget = QWidget()
        controls_widget.setObjectName("controlsWidget")
        controls_widget.setProperty("role", "controlsWidget")
        
        control_layout = QHBoxLayout(controls_widget)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        control_layout.setSpacing(10)

        def add_labeled_widget(label_text, widget: QWidget):
            label = QLabel(label_text)
            label.setObjectName(f"label_{widget.objectName() if widget.objectName() else 'widget'}")
            label.setProperty("role", "dataGraph")
            label.setMaximumWidth(len(label_text) * 10)
            widget.setProperty("role", "dataGraph")
            control_layout.addWidget(label)
            control_layout.addWidget(widget)
        
        # Graph Limit
        self.graph_limit = CustomSpinBox(width=100, value=10, parent=self)
        self.graph_limit.setObjectName("graphLimitSpinBox")
        self.graph_limit.setProperty("role", "graphLimit")
        add_labeled_widget("Limit :", self.graph_limit)

        # Date Range
        self.data_range = DateRangeLineEdit(width=200, func=self.load_by_date, date_now=True, parent=self)
        self.data_range.setObjectName("dataRangeLineEdit")
        self.data_range.setProperty("role", "dataGraph")
        add_labeled_widget("Timeframe :", self.data_range)

        # SAP Input
        sap_list = self.database.get_sap_number()
        self.sap_input = CustomDropdown(sap_list, 100, parent=self)
        self.sap_input.setObjectName("sapInputComboBox")
        self.sap_input.setProperty("role", "dataGraph")
        add_labeled_widget("SAP No. :", self.sap_input)

        # Function Select
        self.function_select = CustomDropdown(["BHW Serial", "SAP Number", "SAP Contributor"], 150, parent=self)
        self.function_select.setObjectName("functionSelectComboBox")
        self.function_select.setProperty("role", "dataGraph")
        self.function_select.setToolTip("""
            BHW Serial      : Graph all BHW Serial on date range.
            SAP Number      : Graph all SAP Number in history.
            SAP Contributor : Graph all BHW Serial on date range using selected SAP Number.
            """)
        add_labeled_widget("Function :", self.function_select)

        # Generate Button
        self.generate_plot = QPushButton("Generate")
        self.generate_plot.setObjectName("generatePlotButton")
        self.generate_plot.setFixedWidth(200)
        self.generate_plot.setProperty("role", "dataGraph")
        self.generate_plot.clicked.connect(self.generate_graph)

        control_layout.addSpacing(20)
        control_layout.addWidget(self.generate_plot)
        
        main_layout.addWidget(controls_widget)

    def load_by_date(self):
        text = self.data_range.text()
        if not text or " - " not in text:
            return None, None
        return text.split(" - ")

    def load_sample_data(self):
        """Load sample data on startup"""
        sample_data = {
            "categories": ["Product A", "Product B", "Product C", "Product D", "Product E", "Product F", "Product G"],
            "bar_data": [42, 68, 55, 89, 73, 61, 47],
            "line_data": ["125.50", "234.00", "189.75", "312.20", "267.30", "198.40", "156.80"],
            "right_label": "Revenue (€)",
            "left_label": "Units Sold",
            "top_label": "📊 Sample Product Performance Dashboard",
            "bottom_label": "Sample Data Analysis - Q4 2024"
        }
        
        # Remove placeholder
        self.remove_placeholder()
        
        # Create the HTML-based graph with sample data
        self.plot_window = GraphData(
            sample_data["categories"],
            sample_data["bar_data"],
            sample_data["line_data"],
            sample_data["right_label"],
            sample_data["left_label"],
            sample_data["top_label"],
            sample_data["bottom_label"]
        )
        self.plot_window.setObjectName("graphPlotWindow")
        
        # Remove existing widgets from the graph layout
        while self.graph_layout.count():
            item = self.graph_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.graph_layout.addWidget(self.plot_window)
        self.current_graph_widget = self.plot_window
        
        # Update the date range to show sample period
        from PyQt6.QtCore import QDate
        from datetime import datetime, timedelta
        
        # Set date range to last 30 days
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-30)
        self.data_range.setText(f"{start_date.toString('yyyy-MM-dd')} - {end_date.toString('yyyy-MM-dd')}")
        
        # Set default values for other fields
        self.graph_limit.setValue(10)
        self.function_select.setCurrentText("BHW Serial")
        
        print("📊 Sample data loaded successfully!")

    def generate_graph(self):
        if self.main_parent:
            self.main_parent.show_notification("Data loading please wait.")
        self.remove_graph()
        start_date, end_date = self.load_by_date()
        if not start_date or not end_date:
            QMessageBox.warning(self, "Invalid Date", "Please select a valid date range.")
            return

        func = self.function_select.currentText()
        selected_sap = self.sap_input.text()

        self.graph_thread = QThread()
        self.worker = GraphWorker(func, start_date, end_date, selected_sap, self.database)
        self.worker.moveToThread(self.graph_thread)

        self.graph_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_graph_ready)
        self.worker.error.connect(self.on_graph_error)
        self.worker.finished.connect(self.graph_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.graph_thread.finished.connect(self.graph_thread.deleteLater)

        self.graph_thread.start()

    def on_graph_ready(self, result):
        try:
            limit = int(self.graph_limit.value())
        except ValueError:
            limit = 30

        # Limit the data (take the top 'limit' items which are already sorted descending)
        for key in ["categories", "bar_data", "line_data"]:
            if key in result and len(result[key]) > limit:
                result[key] = result[key][:limit]

        if result["categories"]:
            # Remove placeholder if exists
            self.remove_placeholder()
            
            # Create the HTML-based graph
            self.plot_window = GraphData(
                result["categories"],
                result["bar_data"],
                result["line_data"],
                result["right_label"],
                result["left_label"],
                result["top_label"],
                result["bottom_label"]
            )
            self.plot_window.setObjectName("graphPlotWindow")
            
            # Remove existing widgets from the graph layout
            while self.graph_layout.count():
                item = self.graph_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            self.graph_layout.addWidget(self.plot_window)
            self.current_graph_widget = self.plot_window
        else:
            QMessageBox.information(self, "No Data", "No data found for the selected filters.")

    def on_graph_error(self, message):
        QMessageBox.critical(self, "Graph Error", f"An error occurred:\n{message}")

    def remove_placeholder(self):
        """Remove the placeholder label if it exists"""
        if hasattr(self, 'placeholder_label') and self.placeholder_label:
            try:
                self.graph_layout.removeWidget(self.placeholder_label)
                self.placeholder_label.deleteLater()
                self.placeholder_label = None
            except:
                pass

    def remove_graph(self):
        """Remove the current graph from the layout"""
        # Remove placeholder if exists
        self.remove_placeholder()
        
        if self.current_graph_widget:
            self.graph_layout.removeWidget(self.current_graph_widget)
            self.current_graph_widget.deleteLater()
            self.current_graph_widget = None
        else:
            # Clear the layout
            while self.graph_layout.count():
                item = self.graph_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Re-add placeholder
            if not hasattr(self, 'placeholder_label') or not self.placeholder_label:
                self.placeholder_label = QLabel("📊 Generate a graph to see data visualization")
                self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.placeholder_label.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        color: #95a5a6;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 40px;
                    }
                """)
            self.graph_layout.addWidget(self.placeholder_label)