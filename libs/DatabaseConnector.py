import sqlite3
import os
import re

class DatabaseConnector:
    def __init__(self):
        # Use raw string to avoid escape sequence issues
        self.base_path = r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\DATA"

        # Check and create directory
        if not os.path.exists(self.base_path):
            try:
                os.makedirs(self.base_path)  # Create directory
                print(f"Created directory: {self.base_path}")
            except PermissionError as e:
                print(str(e))

        # Database path
        self.db_path = os.path.join(self.base_path, "POGOINSERTION.db")
        #print(f'Database path: {self.db_path}')

    def connect(self):
        '''Connect to the SQLite database.'''
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Critical: Error connecting to SQLite database: {e}")
            return None

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        '''Execute SQL query with optional fetching options.'''
        conn = self.connect()
        if conn is None:
            return None  # Return None if connection failed

        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None  # For INSERT, UPDATE, DELETE queries
            conn.commit()
            return result
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
            return None
        finally:
            conn.close()

    def create_tables_if_not_exist(self):
        '''Define and create tables if they don't exist.'''
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

        conn = self.connect()
        if conn is None:
            return  # Return if connection failed

        try:
            cursor = conn.cursor()
            for table_name, columns in tables.items():
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
                cursor.execute(query)
                print(f"INFO: Table '{table_name}' created or already exists.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            print(f'Database path: {self.db_path}')
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

    ##############################################################################
    #####                           LB QUERY                                 #####
    ##############################################################################

    def get_all_lb(self):
        """Get all loadboards and return as a list of strings."""
        result = self.execute_query(query="SELECT LOADBOARDS FROM LOADBOARDS", fetch_all=True)
        return [row[0] for row in result] if result else []

        


    ##############################################################################
    #####                           SAP QUERY                                #####
    ##############################################################################

    def get_sap_number(self):
        """Get SAP numbers and return as list of string."""
        result = self.execute_query(query="SELECT SAPNUMBER FROM SAPNUMBER", fetch_all=True)
        return [row[0] for row in result] if result else []
    
    def get_sap_price(self, sap):
        """Get SAP numbers price and return as list of string."""
        # result = self.execute_query(query="SELECT PRICE FROM SAPNUMBER", fetch_all=True)
        result = self.execute_query(query="SELECT PRICE FROM SAPNUMBER WHERE  SAPNUMBER = ?", params=(sap,), fetch_all=True)
        return [row[0] for row in result] if result else []
    
    def get_all_sap(self):
        """Get SAP numbers details and return as list of string."""
        return self.execute_query(query="SELECT * FROM SAPNUMBER", fetch_all=True)
    
    def delete_sap_number(self, sap):
        """Delete SAP numbers details"""
        self.execute_query(query="DELETE FROM SAPNUMBER WHERE SAPNUMBER = ?", params=(sap,))

    def insert_sap_and_details(self, data):
        """Insert SAP and Details"""
        query = 'INSERT INTO SAPNUMBER (SAPNumber, Price, Comment, GETPN, WinwayPN, Qualmax, MultitestPN, FASASRMRASCOLTXPN, Joshtech) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        return self.execute_query(query, data)
    
    def delete_all_sap_number(self):
        """Delete all from sap number"""
        query = 'DELETE FROM SAPNUMBER'
        return self.execute_query(query)
    


    ##############################################################################
    #####                           Mailer QUERY                             #####
    ##############################################################################

    def get_recepients(self):
        print("INFO: Get Recepients")
        query = f'SELECT * FROM RECEPINENTS ORDER BY STATUS ASC'
        return self.execute_query(query, fetch_all=True)

    ##############################################################################
    #####                           LOGIN QUERY                              #####
    ##############################################################################

    def add_user(self, user, hashed_password):
        '''Add a new user to the credentials table'''
        query = "INSERT INTO credentials (user, password) VALUES (?, ?)"
        params = (user, hashed_password)
        self.execute_query(query, params)

    def update_password(self, user, hashed_password):
        '''Update password for an existing user'''
        query = "UPDATE credentials SET password = ? WHERE user = ?"
        params = (hashed_password, user)
        self.execute_query(query, params)

    def user_exists(self, user):
        '''Check if a user already exists'''
        query = "SELECT 1 FROM credentials WHERE user = ?"
        params = (user,)
        result = self.execute_query(query, params, fetch_all=True)
        return bool(result)

    def check_user(self, user, hashed_password):
        '''Verify if username and password match'''
        query = "SELECT 1 FROM credentials WHERE user = ? AND password = ?"
        params = (user, hashed_password)
        result = self.execute_query(query, params, fetch_all=True)
        return bool(result)

    def create_primary_user(self, hashed_password):
        '''Create default admin user if not exists'''
        if not self.user_exists('admin'):
            print("INFO: Creating Primary Admin User")
            query = "INSERT INTO credentials (user, password) VALUES (?, ?)"
            params = ('admin', hashed_password)
            self.execute_query(query, params)


    ##############################################################################
    #####                           HISTORY QUERY                            #####
    ##############################################################################

    def get_last_use_sap(self, bhw):
        """Get last SAP number used by a specific loadboard."""
        result = self.execute_query(query="SELECT SAPNUMBER FROM POGOINSERTION WHERE BHWName = ? ORDER BY ID DESC LIMIT 1", params=(bhw,), fetch_one=True)
        return str(result[0] if result else None)
    

    def get_convert_history(self):
        """Get all entries from history and extract unique tokens including numbers and symbols."""
        query = "SELECT * FROM POGOINSERTION"
        result = self.execute_query(query, fetch_all=True)

        if result:
            all_tokens = []

            for row in result:
                for item in row:
                    if item:
                        text = str(item)
                        # Extract words including digits and symbols like #, @, comma, etc.
                        tokens = re.findall(r'[\w#@.,&/-]+', text)
                        all_tokens.extend(tokens)

            # Get unique tokens, case-insensitive
            unique_tokens = sorted(set(token.lower() for token in all_tokens))
            return unique_tokens

        return []

    def insert_history(self, bhw_name, date_replaced, run_count, sap_number, qty_of_pogo, price, site, replace_by, remarks):
        print("INFO: Insert History")
        query = 'INSERT INTO POGOINSERTION (BHWName, DateReplaced, RunCount, SapNumber, QtyOfPogo, PogoPrice, Site, ReplaceBy, Remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.execute_query(query, (bhw_name, date_replaced, run_count, sap_number, qty_of_pogo, price, site, replace_by, remarks))

    def get_all_history(self, limit):
        """Get all history data"""
        return self.execute_query(query=f"SELECT * FROM POGOINSERTION ORDER BY ID DESC LIMIT {limit}", 
            fetch_all=True)
    
    def get_bhw_history(self, bhw_pattern, command):
        """Get BHW history from database using pattern matching or exact match"""
        if command == "like":
            return self.execute_query(
                query="SELECT * FROM POGOINSERTION WHERE BHWName LIKE ? ORDER BY ID ASC",
                params=(f"%{bhw_pattern}%",),
                fetch_all=True
            )
        else:
            return self.execute_query(
                query="SELECT * FROM POGOINSERTION WHERE BHWName = ? ORDER BY ID ASC",
                params=(bhw_pattern,),
                fetch_all=True
            )

    def get_bhw_history_in_range(self, start_date, end_date):
        """
        Query records where DateReplaced is between start_date and end_date (inclusive).

        :param start_date: Start date as a string, e.g. '2023-01-01'
        :param end_date: End date as a string, e.g. '2023-12-31'
        :return: List of rows matching the criteria
        """
        print(f"INFO: Query records from {start_date} to {end_date}")
        query = '''
            SELECT * FROM POGOINSERTION
            WHERE DateReplaced BETWEEN ? AND ?
            ORDER BY DateReplaced
        '''
        results = self.execute_query(query, params=(start_date, end_date), fetch_all=True)
        return results
