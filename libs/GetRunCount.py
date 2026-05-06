import oracledb
from PyQt6.QtCore import QThread, pyqtSignal


class GetRunCount(QThread):
    result_runcount = pyqtSignal(str)
    message_on_process = pyqtSignal(str)

    def __init__(self, hardwaretyp: str):
        super().__init__()
        self.hardwaretyp = hardwaretyp

    def run(self) -> None:
        try:
            self.message_on_process.emit("Getting runcount 🔃")
            
            # Parse hardware type and name
            if not self.hardwaretyp.startswith("TOWER"):
                hardwaretyp_name = self.hardwaretyp[:10]
                name = self.hardwaretyp[-6:]
                print("[Info] Common LB detected.")
            else:
                hardwaretyp_name = "Centaur_EX"
                name = self.hardwaretyp
                print("[Info] Tower detected.")

            print(f"[Info] Querying: hardwaretyp_name={hardwaretyp_name}, name={name}")

            # Try different TNS entries
            tns_entries = ['TDIDBPROD.AMSINT.COM', 'TDIDBPROD']
            config_dir = r'C:\app\oracle'
            
            connection = None
            last_error = None
            
            for tns_entry in tns_entries:
                try:
                    print(f"[Info] Trying TNS entry: {tns_entry}")
                    connection = oracledb.connect(
                        user='be_rep',
                        password='berep98',
                        dsn=tns_entry,
                        config_dir=config_dir
                    )
                    print(f"[Info] Successfully connected with: {tns_entry}")
                    break
                except Exception as e:
                    last_error = e
                    print(f"[Info] Failed with {tns_entry}: {e}")
                    continue
            
            if connection is None:
                raise Exception(f"Could not connect with any TNS entry. Last error: {last_error}")
            
            # Execute query with bind variables
            sql_query = """
                SELECT runcount 
                FROM tdi_cal_owner.tdi_boardhardwareitem_view 
                WHERE hardwaretyp_name = :hardwaretyp_name 
                AND name = :name
            """
            
            cursor = connection.cursor()
            cursor.execute(sql_query, {
                'hardwaretyp_name': hardwaretyp_name,
                'name': name
            })
            
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            if not results:
                print("[Warning] No result found in the database.")
                self.result_runcount.emit(None)
                return
            
            # Return the runcount value(s)
            output = '\n'.join(str(row[0]) for row in results)
            print(f"Runcount found: {output}")
            self.result_runcount.emit(output)

        except oracledb.Error as db_error:
            error_obj, = db_error.args
            print(f"[Database Error] {error_obj.message}")
            self.result_runcount.emit(None)
        except Exception as e:
            print(f"[Exception] {e}")
            self.result_runcount.emit(None)