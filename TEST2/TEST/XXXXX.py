    def extract_data(self, tab_widget):
        layout = QVBoxLayout()

        self.graph_frame = QFrame()  # Frame to hold the graph
        self.graph_layout = QVBoxLayout(self.graph_frame)  # Layout inside the frame

        self.date_from = QDateEdit()
        self.date_to = QDateEdit()

        # Set default values
        default_date_to = datetime.datetime.now().date()
        default_date_from = default_date_to - datetime.timedelta(days=1)
        self.date_to.setDate(default_date_to)
        self.date_from.setDate(default_date_from)

        self.date_from.setCalendarPopup(True)  # Enable popup calendar
        self.date_to.setCalendarPopup(True)    # Enable popup calendar

        # Create combo box
        options = ["BHW Name", "SAP Number", "SAP Contributor"]
        self.filter_combo = QComboBox()
        for option in options:
            self.filter_combo.addItem(option)
        self.filter_combo.currentIndexChanged.connect(self.tab_changed_or_index_change)
        
        self.generate_graph_button = QPushButton("Graph Data")
        self.generate_graph_button.setStyleSheet("background-color: green; color: white;")  # Set background color and text color
        self.remove_graph_button = QPushButton("Remove Graph")
        self.remove_graph_button.setStyleSheet("background-color: red; color: white;")  # Set background color and text color
        layout.addWidget(self.graph_frame)
        filter_layout = QHBoxLayout()  # Horizontal layout for filter elements
            
        # Other input fields        
        filter_layout.addWidget(ColoredLabel("Startdatum:  ", 0))
        self.date_from = QDateEdit()
        self.date_from.setDisplayFormat('yyyy-MM-dd')
        self.date_from.setDate(QDate.currentDate().addDays(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setMaximumDate(QDate.currentDate())
        self.date_from.setMaximumHeight(22)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(ColoredLabel("Enddatum:  ", 0))
        self.date_to = QDateEdit()
        self.date_to.setDisplayFormat('yyyy-MM-dd')
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setMaximumDate(QDate.currentDate())
        self.date_to.setMaximumHeight(22)
        filter_layout.addWidget(self.date_to)

        filter_layout.addWidget(ColoredLabel("Sap Number:  ", 0))
        data = self.database.get_column_values('SAPNUMBER', 'SAPNUMBER')
        sap_numbers = [item[0] for item in data]
        self.sap_number_extract = QComboBox()
        self.sap_number_extract.clear()
        self.sap_number_extract.addItems(sap_numbers)
        self.sap_number_extract.setFixedWidth(100)
        filter_layout.addWidget(self.sap_number_extract)

        top_layout = QHBoxLayout()
        top_label = ColoredLabel("Top:  ", 0)
        top_layout.addWidget(top_label)
        self.top = QSpinBox()
        self.top.setValue(10)
        self.top.setMaximum(100)  # Set maximum value
        self.top.setMinimum(1)
        self.top.setFixedWidth(70)
        top_layout.addWidget(self.top)

        # Connect the valueChanged signal to the handle_top_value_changed function
        self.top.valueChanged.connect(self.generate_graph)

        # filter_layout.addLayout(top_layout) #remove 07-22-24 redundunt funtion
        filter_layout.addWidget(ColoredLabel("Filter By:  ", 0))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(self.generate_graph_button)
        filter_layout.addWidget(self.remove_graph_button) #remove 08-22-24 redundunt function graph will auto remove when new is available
        layout.addLayout(filter_layout)

        tab_widget.setLayout(layout)
        
        self.generate_graph_button.clicked.connect(self.generate_graph)
        self.remove_graph_button.clicked.connect(self.remove_graph)

    def generate_graph(self):
        
        self.showMaximized()
        # Initialize empty lists
        categories = []
        bar_data = []
        line_data = []
        date_from = self.date_from.date().toString('yyyy-MM-dd')
        date_to = self.date_to.date().toString('yyyy-MM-dd')

        # Clear previous graph if it exists
        for i in reversed(range(self.graph_layout.count())):
            widget = self.graph_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Determine filter selection and retrieve data
        if self.filter_combo.currentIndex() == 0:
            # Fetch data based on date range
            data = self.database.grap_by_bhw(date_from, date_to)

            if data:
                for LB, SAP, qty in data:
                    price = self.database.get_sap_price(SAP)
                    if price is None:
                        print(f"Price not found for SAP: {SAP}")
                        price = 0  # Default value if price is not found

                    try:
                        total_price = float(qty) * float(price)
                    except ValueError:
                        print(f"Invalid data: qty='{qty}', price='{price}'")
                        total_price = 0

                    categories.append(LB)
                    bar_data.append(int(qty))
                    line_data.append("{:.2f}".format(total_price))
                
                right_label = 'Total Price in Euro'
                left_label = 'Pogo Pin Qty.'
                top_label = f'SAP number Quantity and price {date_from} to {date_to}'
                bottom_label = 'SAP Number'
            else:
                print("No data returned from grap_by_bhw")

        elif self.filter_combo.currentIndex() == 1:
            print("Filter index 1 selected")
            data = self.database.get_sap_use(date_from, date_to)
            print(f"SAP NO> {data}")

            unique_saps = list({sap for sap, in data})  # Ensure SAP numbers are unique and correctly extracted

            if unique_saps:
                for sap_number in unique_saps:
                    # Fetch price and quantity
                    price = self.database.get_sap_price(sap_number)
                    qty = self.database.get_total_pogo_use(date_from, date_to, sap_number)

                    if price is None or qty is None:
                        print(f"Error: Missing data for SAPNumber: {sap_number}")
                        continue  # Skip this iteration

                    try:
                        total_price = float(price) * float(qty)
                    except ValueError:
                        print(f"Invalid data: price='{price}', qty='{qty}'")
                        total_price = 0
                    
                    categories.append(sap_number)
                    bar_data.append(int(qty))
                    line_data.append("{:.2f}".format(total_price))
                
                right_label = 'Total Price in Euro'
                left_label = 'Pogo Pin Qty.'
                top_label = f'Hardware Quantity and Price from {date_from} to {date_to}'
                bottom_label = 'Hardware'
            else:
                print("No unique SAP numbers found in the data")

        elif self.filter_combo.currentIndex() == 2:
            print("Filter index 2 selected")
            selected_sap = self.sap_number_extract.currentText()
            data = self.database.get_lb_use_sap(date_from, date_to, selected_sap)
            print(f"Load Boards: {data}")

            if data:
                for lb in data:
                    pogo_use = self.database.get_lb_total_use(date_from, date_to, lb)
                    price = self.database.get_sap_price(selected_sap)

                    if price is None or pogo_use is None:
                        print(f"Error: Missing data for LB: {lb}")
                        continue  # Skip this iteration

                    try:
                        total_price = float(pogo_use) * float(price)
                    except ValueError:
                        print(f"Invalid data: pogo_use='{pogo_use}', price='{price}'")
                        total_price = 0
                    
                    categories.append(lb)
                    bar_data.append(int(pogo_use))
                    line_data.append("{:.2f}".format(total_price))
                
                right_label = 'Total Price in Euro'
                left_label = 'Pogo Pin Qty.'
                top_label = f'SAP no. {selected_sap} used in different loadboards from {date_from} to {date_to}'
                bottom_label = 'Hardware'
            else:
                print("No load boards found for the selected SAP")

        # Create and display the plot within the graph_frame
        if categories and bar_data and line_data:
            self.plot_window = PlotWindow(categories, bar_data, line_data, right_label, left_label, top_label, bottom_label)
            self.plot_window.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.plot_window.customContextMenuRequested.connect(self.show_context_menu)

            self.current_graph_canvas = self.plot_window.canvas  # Keep reference for context menu
            self.graph_layout.addWidget(self.plot_window)
        else:
            show_message_box([('No data to plot.', "red")], 'information')
            print("No data to plot.")

    def remove_graph(self):
        if self.current_graph_canvas is not None:
            self.graph_layout.removeWidget(self.current_graph_canvas)
            self.current_graph_canvas.deleteLater()
            self.current_graph_canvas = None

    def show_context_menu(self, point):
        context_menu = QMenu(self)
        copy_action = QAction("Copy Graph", self)
        copy_action.triggered.connect(self.copy_graph)
        context_menu.addAction(copy_action)
        context_menu.exec(self.current_graph_canvas.mapToGlobal(point))

    def copy_graph(self):
        buffer = BytesIO()
        self.current_graph_canvas.figure.savefig(buffer, format="png")
        img = QImage.fromData(buffer.getvalue())
        QApplication.clipboard().setImage(img, mode=QClipboard.Mode.Clipboard)

