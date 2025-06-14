import subprocess
import os
import platform

# === Configuration ===
script_path = "RccAuto.py"
icon_path = r"ICON\SP_TitleBarMenuButton.png"
output_dir = "EXE"

# List of extra files or folders to include (source, destination_inside_exe)
extra_files = [
    (r"bin", "bin"),  # <-- Add your bin folder here
]

def is_windows():
    return platform.system().lower() == "windows"

def add_data_files(files):
    """Convert (src, dst) pairs to --add-data strings"""
    sep = ";" if is_windows() else ":"
    options = []
    for src, dst in files:
        src = os.path.abspath(src)
        options.append(f"--add-data={src}{sep}{dst}")
    return options

# === Build command ===
pyinstaller_command = [
    "pyinstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    f"--icon={icon_path}",
    f"--name=RccAutoCreator",
    script_path,
]

# Add data files
pyinstaller_command += add_data_files(extra_files)

# Add output dir
if output_dir:
    pyinstaller_command.append(f"--distpath={output_dir}")

# === Run ===
try:
    subprocess.run(pyinstaller_command, check=True)
    print("✅ Executable created successfully!")
except subprocess.CalledProcessError as e:
    print(f"❌ Error during compilation: {e}")
except FileNotFoundError:
    print("❌ PyInstaller not found. Please install it using 'pip install pyinstaller'.")
