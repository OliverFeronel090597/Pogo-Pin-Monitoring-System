import os

# === Configuration ===
bin_folder = "bin"
keep_files = {
    "rcc.exe",
    "Qt6Core.dll",
    "libstdc++-6.dll",
    "libwinpthread-1.dll",
    "libgcc_s_seh-1.dll",
}

# Normalize filenames for case-insensitive match on Windows
keep_files = {f.lower() for f in keep_files}

# === File Cleanup ===
if not os.path.isdir(bin_folder):
    print(f"❌ Folder not found: {bin_folder}")
else:
    deleted = []
    for fname in os.listdir(bin_folder):
        fpath = os.path.join(bin_folder, fname)
        if os.path.isfile(fpath) and fname.lower() not in keep_files:
            try:
                os.remove(fpath)
                deleted.append(fname)
            except Exception as e:
                print(f"⚠️ Failed to delete {fname}: {e}")

    if deleted:
        print("🧹 Deleted files:")
        for f in deleted:
            print(f"  - {f}")
    else:
        print("✅ Nothing to delete. `bin/` folder is clean.")
