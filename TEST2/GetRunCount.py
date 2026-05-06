import os

import oracledb


def get_runcount(hardwaretyp: str):
    """
    Get runcount from Oracle database using pure Python (no VBS required)
    """
    try:
        print("Getting runcount 🔃")
        
        # Parse hardware type and name
        if not hardwaretyp.startswith("TOWER"):
            hardwaretyp_name = hardwaretyp[:10]
            name = hardwaretyp[-6:]
            print("[Info] Common LB detected.")
        else:
            hardwaretyp_name = "Centaur_EX"
            name = hardwaretyp
            print("[Info] Tower detected.")
        
        print(f"[Info] Querying: hardwaretyp_name={hardwaretyp_name}, name={name}")
        
        # Set the directory containing tnsnames.ora
        tns_config_dir = r"C:\app\oracle"
        
        # Use the correct TNS entry name (with .AMSINT.COM)
        dsn = 'TDIDBPROD.AMSINT.COM'
        
        print(f"[Info] Connecting using TNS entry: {dsn}")
        print(f"[Info] TNS config directory: {tns_config_dir}")
        
        # Connect using python-oracledb Thin mode
        connection = oracledb.connect(
            user='be_rep',
            password='berep98',
            dsn=dsn,
            config_dir=tns_config_dir
        )
        
        # Execute query with bind variables (safe from SQL injection)
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
            return None
        
        # Return runcount value(s)
        if len(results) == 1:
            return str(results[0][0])
        else:
            return '\n'.join(str(row[0]) for row in results)
        
    except oracledb.Error as db_error:
        error_obj, = db_error.args
        print(f"[Database Error] {error_obj.message}")
        return None
    except Exception as e:
        print(f"[Exception] {e}")
        return None


# Even simpler version with hardcoded paths
def get_runcount_simple(hardwaretyp: str):
    """Simplified version with discovered paths"""
    try:
        print("Getting runcount 🔃")
        
        # Parse hardware type and name
        if not hardwaretyp.startswith("TOWER"):
            hardwaretyp_name = hardwaretyp[:10]
            name = hardwaretyp[-6:]
            print("[Info] Common LB detected.")
        else:
            hardwaretyp_name = "Centaur_EX"
            name = hardwaretyp
            print("[Info] Tower detected.")
        
        print(f"[Info] Querying: hardwaretyp_name={hardwaretyp_name}, name={name}")
        
        # Direct connection using the discovered TNS entry
        connection = oracledb.connect(
            user='be_rep',
            password='berep98',
            dsn='TDIDBPROD.AMSINT.COM',  # Full TNS name from tnsnames.ora
            config_dir=r'C:\app\oracle'   # Directory containing tnsnames.ora
        )
        
        cursor = connection.cursor()
        cursor.execute("""
            SELECT runcount 
            FROM tdi_cal_owner.tdi_boardhardwareitem_view 
            WHERE hardwaretyp_name = :hardwaretyp_name 
            AND name = :name
        """, {'hardwaretyp_name': hardwaretyp_name, 'name': name})
        
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if not results:
            print("[Warning] No result found in the database.")
            return None
        
        return str(results[0][0])
        
    except Exception as e:
        print(f"[Error] {e}")
        return None


# Test it
if __name__ == "__main__":
    result = get_runcount_simple("14974-DF02-A1-001")
    if result:
        print(f"Runcount: {result}")
    else:
        print("No result found")

# 14974-DF02-A1-001
# 14974-DF02-A1-002
# 14974-DF02-A1-003
# 14974-DF02-A1-004
# 17134-LB01-A0-001
# 17134-LB01-A0-004
# 17134-LB01-B0-001
# 17203-DF01-A0-002
# 17208-DF01-A0-002
# 17208-DF01-A0-003
# 17450-LB03-A1-001
# 17450-LB03-A1-002
# 17450-LB04-B0-001
# 17450-LB04-B0-008
# 17450-LB05-A0-001
# 17450-LB05-A0-004
# 17452-LB01 A0-001
# 17640-DF01-A0-003
# 17640-DF01-A0-004
# 17640-DF01-A0-005
# 17640-DF01-A0-006
