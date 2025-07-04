# GlobalVarialbles.py

class GlobalState:
    app_version = "5.0.0"
    admin_access = False
    made_changes = False
    log_file_path = rf"\\fsph01\Public\AMS_PHI\12_OPERATIONS\TEST_PRODUCT_ENGINEERING\TPE-Loadboard-Probeshop_Sustaining\Tools\LoadBoardMonitoring\DATA\restriction_logs\error_log.txt"          # Set up exception handling location
    database_path = rf"\\fsph01\Public\AMS_PHI\12_OPERATIONS\TEST_PRODUCT_ENGINEERING\TPE-Loadboard-Probeshop_Sustaining\Tools\LoadBoardMonitoring\DATA\database"
    backup_directory_path = [rf'\\fsphdata\Public\AMS_PHI\12_OPERATIONS\TEST_PRODUCT_ENGINEERING\TPE-Loadboard-Probeshop_Sustaining\Tools\LoadBoardMonitoring\backup',      # Main Backup
                        rf'\\fsph01\Public\AMS_PHI\12_OPERATIONS\TEST_PRODUCT_ENGINEERING\TPE-Loadboard-Probeshop_Sustaining\Tools\LoadBoardMonitoring\backup\DONT_DELETE!']  # Developer backup in case of data loss - remove as they cant access tdis location axcept TPE
                     

    @classmethod
    def reset(cls):
        #clas.varname = etc
        pass