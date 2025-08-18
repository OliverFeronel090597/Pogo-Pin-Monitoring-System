import sys
import os

def get_path(relative_path):
    """
    Get the absolute path to a resource, whether the application is running 
    as a standalone script or as a PyInstaller-compiled executable.

    This ensures that resource files (e.g., images, config files) can be 
    reliably accessed in both development and packaged environments.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    try:
        # Path used when the app is run as a PyInstaller bundle
        base_path = sys._MEIPASS
    except AttributeError:
        # Path used when the app is run as a standard Python script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
