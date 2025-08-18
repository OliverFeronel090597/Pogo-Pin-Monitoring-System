'''
sqlite3 library to auto connect and disconnect on database
'''

import sqlite3

class SQLite:
    def __init__(self):
        self.db_path = r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\DATA\POGOINSERTION.db"
        self.conn = None
        self.cursor = None
        # self.create_tables_if_not_exist() #moved to main
        # self.fix_id_consecutive()

    def connect(self):
        '''attach to database'''
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"INFO: Connected to SQLite database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Critical: Error connecting to SQLite database: {e}")

    def disconnect(self):
        '''detach to database'''
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
        if self.conn:
            self.conn.close()
            print("Disconnected from SQLite database")
        else:
            print("No connection to SQLite database")

    def execute_query_one(self, query, params=None):
        '''execute SQL query and handle connection'''
        try:
            self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
            return None
        finally:
            self.disconnect()
            
    def create_tables_if_not_exist(self):
        '''Define table names and their columns'''
        tables = {
            "LOADBOARDS": [
                "LOADBOARDS TEXT"
            ],
            "POGOINSERTION": [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",  # Adding the id column as the primary key
                "BHWName TEXT",
                "DateReplaced TIMESTAMP",
                "RunCount TEXT",
                "SapNumber INTEGER",
                "QtyOfPogo INTEGER",
                "PogoPrice REAL",
                "Site TEXT",
                "ReplaceBy TEXT",
                "Remarks TEXT"
            ],
            "CREDENTIALS": [
                "user TEXT UNIQUE",
                "password TEXT"
            ],
            "SAPNUMBER": [
                "SAPNumber TEXT",
                "Price REAL",
                "Comment TEXT",
                "GETPN TEXT",
                "WinwayPN TEXT",
                "Qualmax TEXT",
                "MultitestPN TEXT",
                "FASASRMRASCOLTXPN TEXT",
                "Joshtech TEXT"
            ],
            "RECEPINENTS": [
                "STATUS TEXT",
                "EMAIL TEXT"
            ],
            "OLD_VERSION": [
                "ID INTEGER PRIMARY KEY AUTOINCREMENT",
                "VERSION TEXT"
            ],
            "ANNOUNCEMENT": [
                "ID INTEGER PRIMARY KEY AUTOINCREMENT",
                "DATE TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP",  # Automatically stores the current date and time
                "DETAILS TEXT NOT NULL",  # Title of the announcement
            ]
        }

        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables if they do not exist
        for table_name, columns in tables.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                cursor.execute(f"CREATE TABLE {table_name} ({', '.join(columns)})")
                print(f"INFO: Table '{table_name}' created successfully.")
            else:
                print(f"INFO: Table '{table_name}' already exists.")

        conn.commit()
        conn.close()
                
    def fix_id_consecutive(self):
        ''' Renumber IDs to ensure a consecutive sequence and update sqlite_sequence '''
        try:
            # Connect to the SQLite database
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Step 1: Fetch the current IDs in ascending order
            cursor.execute("SELECT ID FROM POGOINSERTION ORDER BY ID ASC")
            rows = cursor.fetchall()

            # Extract current IDs into a list
            current_ids = [row[0] for row in rows]

            # Step 2: Generate the new ID sequence
            new_ids = list(range(1, len(current_ids) + 1))

            # Temporary phase: Use negative IDs to avoid conflicts
            temp_ids = list(range(-1, -len(current_ids) - 1, -1))

            # Step 3: Update the database using temporary IDs to avoid conflicts
            for current_id, temp_id in zip(current_ids, temp_ids):
                cursor.execute("UPDATE POGOINSERTION SET ID = ? WHERE ID = ?", (temp_id, current_id))

            # Commit the changes to apply temporary IDs
            connection.commit()

            # Step 4: Now update to the final new IDs
            for temp_id, new_id in zip(temp_ids, new_ids):
                cursor.execute("UPDATE POGOINSERTION SET ID = ? WHERE ID = ?", (new_id, temp_id))

            # Commit the final changes
            connection.commit()

            # Step 5: Fetch the new maximum ID after renumbering
            cursor.execute("SELECT MAX(ID) FROM POGOINSERTION")
            max_id = cursor.fetchone()[0]

            # Step 6: Update the sqlite_sequence table to reflect the new max ID
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'POGOINSERTION'", (max_id,))
            
            # Commit the sqlite_sequence update
            connection.commit()

            print("ID values updated successfully and sqlite_sequence updated.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the connection
            connection.close()
                        
    
    def letiral_execute(self, query, params=None):
        try:
            self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
        finally:
            self.disconnect()
                    
            
    def execute_query_all(self, query, params=None):
        '''execute SQL query and handle connection'''
        try:
            self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
            return None
        finally:
            self.disconnect()

    def execute_query_insert(self, query, params=None):
        '''execute SQL query and handle connection'''
        try:
            self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
            return None
        finally:
            self.disconnect()

    def get_unique_column_values(self, table, column):
        print("INFO: get DISTINCT")
        query = f'SELECT DISTINCT {column} FROM {table}'
        return self.execute_query_all(query)

    def get_column_values(self, table, column):
        print("INFO: get Loadboard")
        query = f'SELECT {column} FROM {table}'
        return self.execute_query_all(query)

    def get_last_replace_user(self):
        print("INFO: get user's")
        query = 'SELECT ReplaceBy FROM POGOINSERTION'
        return self.execute_query_all(query)

    def get_sap_data_all(self):
        print("INFO: get SAP Number")
        query = 'SELECT SAPNumber, PRICE, Comment, GETPN, WinwayPN, Qualmax, MultitestPN, FASASRMRASCOLTXPN, Joshtech FROM SAPNUMBER'
        return self.execute_query_all(query)

    def pogo_price_update(self, sap_number):
        print("INFO: Pogo Price Update")
        query = 'SELECT PRICE FROM SAPNUMBER WHERE SAPNumber = ?'
        return self.execute_query_one(query, (sap_number,))

    def insert_loadboard(self, lb):
        print("INFO: Insert New Loadboard")
        query = 'INSERT INTO LOADBOARDS (LOADBOARDS) VALUES (?)'
        self.execute_query_insert(query, (lb,))
        
    def insert_history(self, bhw_name, date_replaced, run_count, sap_number, qty_of_pogo, price, site, replace_by, remarks):
        print("INFO: Insert History")
        query = 'INSERT INTO POGOINSERTION (BHWName, DateReplaced, RunCount, SapNumber, QtyOfPogo, PogoPrice, Site, ReplaceBy, Remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.execute_query_insert(query, (bhw_name, date_replaced, run_count, sap_number, qty_of_pogo, price, site, replace_by, remarks))
        
    def get_last_sap_of_lb(self, lb):
        print("INFO: Get Last SAP Number")
        if len(lb) > 5:
            query = 'SELECT SAPNumber FROM POGOINSERTION WHERE BHWName = ? ORDER BY DateReplaced DESC LIMIT 1'
            return self.execute_query_one(query, (lb,))
    
    def insert_sap_and_details(self, data):
        print("INFO: Insert SAP and Details")
        query = 'INSERT INTO SAPNUMBER (SAPNumber, Price, Comment, GETPN, WinwayPN, Qualmax, MultitestPN, FASASRMRASCOLTXPN, Joshtech) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        return self.execute_query_insert(query, data)
    
    def delete_sap_number(self):
        print("INFO: Delete SAP Number")
        query = 'DELETE FROM SAPNUMBER'
        return self.execute_query_insert(query)
            
    def get_sap_data(self, sap):
        print("INFO: Get SAP Data")
        query = 'SELECT * FROM SAPNUMBER WHERE SAPNumber = ?'
        return self.execute_query_all(query, (sap,))
    
    def get_history(self, limit):
        print("INFO: Get History")
        query = f'SELECT * FROM POGOINSERTION ORDER BY ID DESC LIMIT {limit}'
        return self.execute_query_all(query)

    def get_recepients(self):
        print("INFO: Get Recepients")
        query = f'SELECT * FROM RECEPINENTS ORDER BY STATUS ASC'
        return self.execute_query_all(query)
    
    def get_sap_price(self, sapnumber):
        print("INFO: Get SAP price")
        query = 'SELECT Price FROM SAPNUMBER WHERE SAPNumber = ?'
        results = self.execute_query_all(query, (sapnumber,))
        if results:
            return results[0][0] 
        else:
            print(f"WARNING: No price found for SAPNumber: {sapnumber}")
            return None
        
    def get_max_history_id(self):
        query = "SELECT MAX(ID) FROM POGOINSERTION"
        results = self.execute_query_all(query, params=None)
        if results:
            return results[0][0] 
        else:
            print(f"Cant retrive max ID")
            return None 

    
                                      #################################################
    ##################################     Query for qraphing                          ########################################
                                      #################################################
    def grap_by_bhw(self, date_from, date_to):
        '''Return unique SAP numbers with their corresponding BHWName and QtyOfPogo within the date range.'''
        print(f"INFO: Get Graph Data From {date_from} AND {date_to}")
        query = '''
            SELECT DISTINCT BHWName, SapNumber, QtyOfPogo
            FROM POGOINSERTION
            WHERE DateReplaced BETWEEN ? AND ?
        '''
        # Execute the query and return results
        result = self.execute_query_all(query, (date_from, date_to))
        
        if result:
            return result
        else:
            print(f"Error: Nothing found")
            return []

    def get_data_to_graph_bhw_graph_by_sap_number(self, date_from, date_to, selected_sap_number) -> list:
        '''Get loadboard data according to date range'''
        print("INFO: Get Data to Graph")
        query = 'SELECT BHWName, SapNumber, QtyOfPogo FROM POGOINSERTION WHERE DateReplaced BETWEEN ? AND ? AND SapNumber = ?'
        return self.execute_query_all(query, (date_from, date_to, selected_sap_number))
    
    def get_data_to_graph(self, date_from, date_to) -> list:
        ''''''
        print("INFO: Get Data to Graph")
        query = 'SELECT BHWName, SapNumber, QtyOfPogo FROM POGOINSERTION WHERE DateReplaced BETWEEN ? AND ?'
        return self.execute_query_all(query, (date_from, date_to))
    
    def get_sap_use(self, date_from, date_to):
        '''Get SAP use in time frame'''
        print("INFO: Get SAP use in time frame")
        query = 'SELECT SapNumber FROM POGOINSERTION WHERE DateReplaced BETWEEN ? AND ?'
        
        # Execute the query and return results
        return self.execute_query_all(query, (date_from, date_to))

    def get_total_pogo_use(self, date_from, date_to, sap):
        '''Get Total pogopin use in time frame'''
        print(f"INFO: Total pogo use for SAP: {sap}.")
        query = 'SELECT SUM(QtyOfPogo) FROM POGOINSERTION WHERE SapNumber = ? AND DateReplaced BETWEEN ? AND ?'
        
        # Execute the query and return results
        result = self.execute_query_all(query, (sap, date_from, date_to))
        if result and result[0][0] is not None:
            return result[0][0]
        else:
            print(f"Error: No QtyOfPogo found for SAPNumber: {sap}")
            return None

    def get_lb_use_sap(self, date_from, date_to, sap):
        '''Get all unique LB that use the specified SAP within the time frame.'''
        print("INFO: Get LB use SAP")
        # SQL query to select all BHWName where SapNumber matches and DateReplaced is within the date range
        query = 'SELECT BHWName FROM POGOINSERTION WHERE SapNumber = ? AND DateReplaced BETWEEN ? AND ?'
        # Execute the query and return all results
        result = self.execute_query_all(query, (sap, date_from, date_to))
        if result:
            # Extract all BHWName values and ensure they are unique by using a set
            unique_bhw_names = list(set(row[0] for row in result))
            return unique_bhw_names
        else:
            print(f"Error: No BHWName found for SAPNumber: {sap} in the given date range.")
            return []

    def get_lb_total_use(self, date_from, date_to, lb):
        '''Get total pogo use for a specific LB within the given date range.'''
        print('INFO: Get LB total use for a specific LB')
        # Corrected SQL query to sum the pogo usage for a specific LB within the date range
        query = 'SELECT SUM(QtyOfPogo) FROM POGOINSERTION WHERE BHWName = ? AND DateReplaced BETWEEN ? AND ?'
        # Execute the query and return the result
        result = self.execute_query_all(query, (lb, date_from, date_to))
        if result and result[0][0] is not None:
            # Return the total summed quantity
            return result[0][0]
        else:
            print(f"Error: No pogo usage found for LB: {lb} in the given date range.")
            return 0  # Return 0 instead of an empty list to indicate no usage


    def check_new_his(self):
        '''Check if new added in history every 10 sec'''
        print('INFO: Check if new added in history every 10 sec and update his list')
        query = 'SELECT MAX(ID) FROM POGOINSERTION'
        return self.execute_query_one(query)
        
        
        
                                      #################################################
    ##################################     Query for Login                            ########################################
                                      #################################################
    
    def user_save_update(self, user,  hashed_password):
        '''Save or update user details'''
        print("INFO: Save/Update User Details")
        query = "INSERT OR REPLACE INTO credentials (user, password) VALUES (?, ?)"
        params = (user, hashed_password)  # Use parameterized query
        self.letiral_execute(query, params)  # Assuming `execute_query` is the correct method

    def get_user(self, user):
        '''Get user data'''
        print("INFO: Get User Data")
        query = "SELECT * FROM credentials WHERE user = ?"  # Parameterized query
        params = (user,)  # Single-item tuple
        return self.execute_query_one(query, params)  # Assuming `execute_query_one` is the correct method
    
    def create_primary_user(self, hash_password):
        info_x = '''INFO: Create 1st user if app newly use no database'''
        print(info_x)
        query = "INSERT OR REPLACE INTO credentials (user, password) VALUES (?, ?)"
        params = ('admin', hash_password)  # Use parameterized query
        self.letiral_execute(query, params)  # Assuming `execute_query` is the correct method

                                      #################################################
    ##################################     For Win 11 OSRAM USER                       ########################################
                                      #################################################

    def update_user_data(self, osram, ams):
        info_x = f'''INFO: save update username for win 11 ex, O.Feronel to ofer ||| {osram} --- {ams}'''
        print(info_x)
        query = "INSERT OR REPLACE INTO OSRAM_USER (OSRAM_USER, AMS_USER) VALUES (?, ?)"
        params = (osram, ams)  # Use parameterized query
        self.execute_query_insert(query, params)  # Assuming `execute_query` is the correct method


    def check_osram_user(self, username):
        print("INFO: Get SAP price")
        query = 'SELECT OSRAM_USER FROM OSRAM_USER WHERE OSRAM_USER = ?'
        results = self.execute_query_all(query, (username,))
        if results:
            return results[0][0] 
        else:
            print(f"Cand find user please set AMS user name {username}")
            return None
        
    def get_ams_user(self, username):
        print("INFO: Get SAP price")
        query = 'SELECT AMS_USER FROM OSRAM_USER WHERE OSRAM_USER = ?'
        results = self.execute_query_all(query, (username,))
        if results:
            return results[0][0] 
        else:
            print(f"Cand find user please set AMS user name{username}")
            return None
        

                                      #################################################
    ##################################    Inactive version list                        ########################################
                                      #################################################


    def get_inactive_version(self):
        '''Get inactive versions from the OLD_VERSION table and return them as a list'''
        print("INFO: Fetching inactive versions")
        query = "SELECT VERSION FROM OLD_VERSION"  # Corrected column name
        results = self.execute_query_all(query)  # Fetch results from the database
        
        # Extract versions from the results and return as a list
        return [row[0] for row in results] if results else []

                                      #################################################
    ##################################     ANNOUNCEMENT FOR ANY UPDATE ETC             ########################################
                                      #################################################

    def get_announcement(self):
        """Get the most recent announcement from the ANNOUNCEMENT table."""
        print("INFO: get_announcement")
        query = "SELECT DETAILS, DATE FROM ANNOUNCEMENT ORDER BY ID DESC LIMIT 1;"
        result = self.execute_query_all(query)
        
        if result:  # Check if the result is not empty
            message, date = result[0]  # Unpack the message and date
            print(f"Latest Announcement: {message} (Date: {date})")
            return message, date  # Return both the message and date
        else:
            print("No announcements found.")
            return None, None  # Return None for both message and date if no announcements are found
        


    def update_history(self, record_id, bhw_name, date_replaced, run_count, sap_number, qty_of_pogo, price, site, replace_by, remarks):
        print(f"INFO: Updating History for ID(s): {record_id}")
        query = '''
            UPDATE POGOINSERTION 
            SET BHWName = ?, DateReplaced = ?, RunCount = ?, SapNumber = ?, 
                QtyOfPogo = ?, PogoPrice = ?, Site = ?, ReplaceBy = ?, Remarks = ? 
            WHERE ID IN ({})
        '''.format(','.join(['?'] * len(record_id)))  # Dynamically create placeholders for multiple IDs
        self.execute_query_insert(query, (bhw_name, date_replaced, run_count, sap_number, qty_of_pogo, price, site, replace_by, remarks, *record_id))
