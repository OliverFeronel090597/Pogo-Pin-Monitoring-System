from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QClipboard, QImage
from io import BytesIO
from libs.CalendarLineEdit import DateRangeLineEdit
from libs.CustomComboBox import CustomDropdown
from libs.GraphData import GraphData
from libs.DatabaseConnector import DatabaseConnector

from PyQt6.QtCore import QObject, QThread, pyqtSignal

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
                for lb, sap, qty in data:
                    price_data = self.database.get_sap_price(sap)
                    price = price_data[0] if price_data and price_data[0] is not None else 0
                    try:
                        total = float(qty) * float(price)
                    except ValueError:
                        total = 0
                    result["categories"].append(lb)
                    result["bar_data"].append(int(qty))
                    result["line_data"].append(f"{total:.2f}")

                result["left_label"] = "Pogo Pin Qty."
                result["right_label"] = "Total Price in Euro"
                result["top_label"] = f"BHW Pogo Pin Quantity and Price from {self.start_date} to {self.end_date}"
                result["bottom_label"] = "BHW Serial"

            elif self.func == "SAP Number":
                data = self.database.get_sap_use(self.start_date, self.end_date)
                unique_saps = list({sap for (sap,) in data})
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
                    result["categories"].append(sap)
                    result["bar_data"].append(int(qty))
                    result["line_data"].append(f"{total:.2f}")

                result["left_label"] = "Pogo Pin Qty."
                result["right_label"] = "Total Price in Euro"
                result["top_label"] = f"SAP Number Pogo Pin Quantity and Price from {self.start_date} to {self.end_date}"
                result["bottom_label"] = "SAP Number"

            elif self.func == "SAP Contributor":
                data = self.database.get_lb_use_sap(self.start_date, self.end_date, self.selected_sap)
                if data:
                    for lb in data:
                        pogo_use = self.database.get_lb_total_use(self.start_date, self.end_date, lb)
                        price = self.database.get_sap_price(self.selected_sap)[0]
                        if price is None or pogo_use is None:
                            continue
                        try:
                            total_price = float(pogo_use) * float(price)
                        except ValueError:
                            total_price = 0
                        result["categories"].append(lb)
                        result["bar_data"].append(int(pogo_use))
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
        self.current_graph_canvas = None
        self.main_parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.graph_layout = QVBoxLayout()
        main_layout.addLayout(self.graph_layout)

        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(control_layout)

        def add_labeled_widget(label_text, widget):
            label = QLabel(label_text)
            label.setProperty("role", "dataGraph")
            label.setMaximumWidth(len(label_text) * 10)
            widget.setProperty("role", "dataGraph")
            control_layout.addWidget(label)
            control_layout.addWidget(widget)

        self.data_range = DateRangeLineEdit(width=200, func=self.load_by_date, date_now=True, parent=self)
        add_labeled_widget("Timeframe :", self.data_range)

        sap_list = self.database.get_sap_number()
        self.sap_input = CustomDropdown(sap_list, 200, parent=self)
        add_labeled_widget("SAP No. :", self.sap_input)

        self.function_select = CustomDropdown(["BHW Serial", "SAP Number", "SAP Contributor"], 200, parent=self)
        add_labeled_widget("Function :", self.function_select)

        self.generate_plot = QPushButton("Generate")
        self.generate_plot.setFixedWidth(200)
        self.generate_plot.setProperty("role", "dataGraph")
        self.generate_plot.clicked.connect(self.generate_graph)

        control_layout.addSpacing(20)
        control_layout.addWidget(self.generate_plot)

    def load_by_date(self):
        text = self.data_range.text()
        if not text or " - " not in text:
            return None, None
        return text.split(" - ")

    def generate_graph(self):
        self.main_parent.show_notification("Data loading please wait.")
        self.remove_graph()
        start_date, end_date = self.load_by_date()
        if not start_date or not end_date:
            QMessageBox.warning(self, "Invalid Date", "Please select a valid date range.")
            return

        func = self.function_select.currentText()
        selected_sap = self.sap_input.text()

        self.thread = QThread()
        self.worker = GraphWorker(func, start_date, end_date, selected_sap, self.database)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_graph_ready)
        self.worker.error.connect(self.on_graph_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_graph_ready(self, result):
        categories = result["categories"]
        if len(categories) > 30:
            response = QMessageBox.question(
                self,
                "Too Much Data",
                f"Detected {len(categories)} data points. Show only the last 30?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if response == QMessageBox.StandardButton.Yes:
                for key in ["categories", "bar_data", "line_data"]:
                    result[key] = result[key][-30:]
            else:
                return

        if result["categories"]:
            self.plot_window = GraphData(
                result["categories"],
                result["bar_data"],
                result["line_data"],
                result["right_label"],
                result["left_label"],
                result["top_label"],
                result["bottom_label"]
            )
            self.plot_window.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.plot_window.customContextMenuRequested.connect(self.show_context_menu)
            self.current_graph_canvas = self.plot_window.canvas
            self.graph_layout.addWidget(self.plot_window)
        else:
            QMessageBox.information(self, "No Data", "No data found for the selected filters.")

    def on_graph_error(self, message):
        QMessageBox.critical(self, "Graph Error", f"An error occurred:\n{message}")


    def show_context_menu(self, point):
        menu = QMenu(self)
        copy_action = QAction("Copy Graph", self)
        copy_action.triggered.connect(self.copy_graph)
        menu.addAction(copy_action)
        menu.exec(self.current_graph_canvas.mapToGlobal(point))

    def copy_graph(self):
        buffer = BytesIO()
        self.current_graph_canvas.figure.savefig(buffer, format="png")
        image = QImage.fromData(buffer.getvalue())
        QApplication.clipboard().setImage(image, QClipboard.Mode.Clipboard)

    def remove_graph(self):
        if self.current_graph_canvas:
            self.graph_layout.removeWidget(self.plot_window)
            self.plot_window.deleteLater()
            self.current_graph_canvas = None
