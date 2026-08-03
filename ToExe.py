import os
import platform
import subprocess
import sys

# === Configuration ===
script_path = "PPM_V5.py"
icon_path = r"icon\main-logo.png"
output_dir = "EXE"
python_version = f"py{sys.version_info.major}{sys.version_info.minor}"

# List of extra files or folders to include (source, destination_inside_exe)
extra_files = [
    #(r"bin", "bin"),
    #(r"libs", "libs"),  # Uncomment if you need to include the libs folder
]

# Hidden imports for oracledb and dependencies
hidden_imports = [
    "getpass",
    "oracledb",
    "oracledb.base_impl",
    "oracledb.thin_impl",
    "oracledb.defaults",
    "oracledb.connection",
    "oracledb.cursor",
    "oracledb.pool",
    "oracledb.lob",
    "oracledb.types",
    "oracledb.errors",
    "oracledb.__main__",
    "cx_Oracle",  # In case some code still uses cx_Oracle
    "cryptography",
    "cryptography.hazmat",
    "cryptography.hazmat.primitives",
    "cryptography.hazmat.backends",
]

def is_windows():
    return platform.system().lower() == "windows"

def add_data_files(files):
    """Convert (src, dst) pairs to --add-data strings"""
    sep = ";" if is_windows() else ":"
    options = []
    for src, dst in files:
        src = os.path.abspath(src)
        if os.path.exists(src):
            options.append(f"--add-data={src}{sep}{dst}")
        else:
            print(f"⚠️  Warning: File/Folder not found: {src}")
    return options

def add_hidden_imports(imports):
    """Convert list of imports to --hidden-import strings"""
    options = []
    for imp in imports:
        options.append(f"--hidden-import={imp}")
    return options

# === Build command ===
pyinstaller_command = [
    "pyinstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--clean",  # Clean cache
    f"--icon={icon_path}",
    f"--name=PPMv5.3.0",
]

# Add hidden imports
pyinstaller_command += add_hidden_imports(hidden_imports)

# Add collect submodules
pyinstaller_command.append("--collect-submodules=oracledb")
pyinstaller_command.append("--collect-submodules=cryptography")

# Add the script
pyinstaller_command.append(script_path)

# Add data files
pyinstaller_command += add_data_files(extra_files)

# Add output dir
if output_dir:
    pyinstaller_command.append(f"--distpath={output_dir}")

# Add Windows specific options
if is_windows():
    pyinstaller_command.append("--uac-admin")  # Request admin privileges if needed
    # Add version info if you have it
    # pyinstaller_command.append("--version-file=version.txt")

# === Run ===
try:
    print("🚀 Starting PyInstaller build...")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Script: {script_path}")
    print(f"🖼️  Icon: {icon_path}")
    print(f"🐍 Python version: {python_version}")
    print(f"📦 Hidden imports: {len(hidden_imports)} modules")
    print(f"📂 Extra files: {len(extra_files)} items")
    
    print("\n🔧 Running command:")
    print(" ".join(pyinstaller_command))
    print("\n" + "="*60)
    
    # Run the build
    result = subprocess.run(pyinstaller_command, capture_output=True, text=True)
    
    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n" + "="*60)
        print("✅ Executable created successfully!")
        exe_path = os.path.join(output_dir, "PPMv5.3.0.exe")
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Location: {os.path.abspath(exe_path)}")
            print(f"📦 Size: {size:.2f} MB")
        else:
            print(f"⚠️  Executable not found at expected location: {exe_path}")
    else:
        print("\n" + "="*60)
        print(f"❌ Error during compilation (exit code: {result.returncode})")
        
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error during compilation: {e}")
    if e.stdout:
        print(f"Output: {e.stdout}")
    if e.stderr:
        print(f"Error: {e.stderr}")
except FileNotFoundError:
    print("\n❌ PyInstaller not found. Please install it using:")
    print("   pip install pyinstaller")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")