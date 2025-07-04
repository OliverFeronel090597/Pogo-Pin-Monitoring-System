from PyQt6.QtCore import QDir, QDirIterator

def list_resource_files_by_input():
    """
    Prompts user to input a Qt resource path (like :/resources),
    then lists all files under that path (recursively).
    """
    user_input = input("Enter resource path (e.g., :/resources): ").strip()

    # Make sure it starts with colon
    if not user_input.startswith(":/"):
        print("❌ Invalid path. It must start with `:/`.")
        return

    resource_path = user_input
    if not QDir(resource_path).exists():
        print(f"❌ Path does not exist: {resource_path}")
        return

    it = QDirIterator(resource_path, QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)

    print(f"📦 Files in {resource_path}:")
    while it.hasNext():
        file_path = it.next()
        file_name = file_path.split("/")[-1]
        print(f"  - {file_name}")

list_resource_files_by_input()