import os

def generate_qrc(folder_path, output_qrc="resources.qrc", prefix="/resources"):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    with open(output_qrc, "w", encoding="utf-8") as qrc_file:
        qrc_file.write("<RCC>\n")
        qrc_file.write(f'    <qresource prefix="{prefix}">\n')
        for file in files:
            qrc_file.write(f'        <file>{file}</file>\n')
        qrc_file.write("    </qresource>\n")
        qrc_file.write("</RCC>\n")

    print(f"✅ Generated {output_qrc} with {len(files)} files.")

# Example usage
generate_qrc(r"C:\Users\O.Feronel\OneDrive - ams OSRAM\Documents\PYTHON\RCC_UPGRADE\ICOn\converted_png")
