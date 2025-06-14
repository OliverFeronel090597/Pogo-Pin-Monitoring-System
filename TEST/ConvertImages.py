import os
from PIL import Image

def convert_folder_to_png(folder_path: str):
    supported_extensions = (".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")
    output_folder = os.path.join(folder_path, "converted_png")

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_extensions):
            input_path = os.path.join(folder_path, filename)
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(output_folder, output_filename)
            try:
                with Image.open(input_path) as img:
                    img = img.convert("RGBA")
                    img.save(output_path, "PNG")
                    print(f"✅ Converted: {filename} → {output_filename}")
            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")

# Example usage
convert_folder_to_png(r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\PPM_V5\icon")
