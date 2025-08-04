import win32com.client

DEBUG = True

def log(msg):
    if DEBUG:
        print("[DEBUG]", msg)

def folder_exists(parent, name):
    try:
        _ = parent.Folders[name]
        return True
    except:
        return False

def create_ppm_in_builtin_archive():
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")

    mailbox_name = "oliver.feronel@ams-osram.com"
    archive_folder_name = "Archive"
    ppm_folder_name = "PPM"

    log("Getting mailbox...")
    mailbox = namespace.Folders[mailbox_name]

    if not mailbox:
        log(f"Mailbox '{mailbox_name}' not found.")
        return

    try:
        archive_folder = mailbox.Folders[archive_folder_name]
        log(f"Found Archive folder under '{mailbox_name}'.")
    except:
        log(f"Archive folder '{archive_folder_name}' not found in mailbox.")
        return

    if folder_exists(archive_folder, ppm_folder_name):
        log(f"'{ppm_folder_name}' already exists under Archive.")
        return

    log(f"Creating '{ppm_folder_name}' under Archive...")
    archive_folder.Folders.Add(ppm_folder_name)

    if folder_exists(archive_folder, ppm_folder_name):
        log(f"Confirmed: '{ppm_folder_name}' successfully created under Archive.")
    else:
        log(f"Failed to confirm creation of '{ppm_folder_name}'.")

if __name__ == "__main__":
    create_ppm_in_builtin_archive()
