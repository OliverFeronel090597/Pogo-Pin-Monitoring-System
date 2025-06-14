import subprocess
import os
from PyQt6.QtCore import pyqtSignal, QThread


import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt



vbs_code = """
Const adOpenForwardOnly = 0
Const adLockReadOnly = 1
Const adCmdText = 1

Set Cn = CreateObject("ADODB.Connection")
Set rs = CreateObject("ADODB.Recordset")

xprovider = "OraOledb.Oracle"
datenquelle = "TDIDBPROD"
UserName = "be_rep"
passwort = "berep98"

hardwaretyp_name = WScript.Arguments.Item(0)
name = WScript.Arguments.Item(1)

sqlabfrage = "SELECT * FROM tdi_cal_owner.tdi_boardhardwareitem_view WHERE hardwaretyp_name = '" & hardwaretyp_name & "' AND name = '" & name & "'"

Cn.ConnectionString = "Provider=" & xprovider & ";Password=" & passwort & ";User ID=" & UserName & ";Data Source=" & datenquelle
Cn.Open
rs.Open sqlabfrage, Cn, adOpenForwardOnly, adLockReadOnly, adCmdText

If rs.EOF Then
    WScript.StdOut.WriteLine "No result"
Else
    Do Until rs.EOF
        For i = 0 To rs.Fields.Count - 1
            WScript.StdOut.Write rs.Fields(i).Name & ": "
            If IsNull(rs.Fields(i).Value) Then
                WScript.StdOut.WriteLine "NULL"
            Else
                WScript.StdOut.WriteLine rs.Fields(i).Value
            End If
        Next
        WScript.StdOut.WriteLine "-----"
        rs.MoveNext
    Loop
End If

rs.Close
Cn.Close
Set rs = Nothing
Set Cn = Nothing

"""

class GetRunCount(QThread):
    result_runcount = pyqtSignal(str)
    message_on_process = pyqtSignal(str)

    def __init__(self, hardwaretyp: str):
        super().__init__()
        self.hardwaretyp = hardwaretyp

    def run(self) -> None:
        try:
            self.message_on_process.emit("Getting runcount 🔃")
            if not self.hardwaretyp.startswith("TOWER"):
                hardwaretyp_name = self.hardwaretyp[:10]
                name = self.hardwaretyp[-6:]
                print("[Info] Common LB detected.")
            else:
                hardwaretyp_name = "Centaur_EX"
                name = self.hardwaretyp
                print("[Info] Tower detected.")

            print(f"[Info] Querying: hardwaretyp_name={hardwaretyp_name}, name={name}")

            vbs_file_path = os.path.abspath("fetch_data.vbs")
            with open(vbs_file_path, "w", encoding="utf-8") as f:
                f.write(vbs_code)

            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                ["cscript.exe", "//Nologo", vbs_file_path, hardwaretyp_name, name],
                capture_output=True,
                text=True,
                startupinfo=startup_info,
            )

            try:
                os.remove(vbs_file_path)
            except Exception as e:
                print(f"[Warning] Could not remove temp VBS file: {e}")

            if result.returncode != 0:
                print(f"[Error] Script failed: {result.stderr.strip()}")
                self.result_runcount.emit(None)
                return

            output = result.stdout.strip()
            if output.lower() == "no result":
                print("[Warning] No result found in the database.")
                self.result_runcount.emit(None)
                return

            self.result_runcount.emit(output)

        except Exception as e:
            print(f"[Exception] {e}")
            self.result_runcount.emit(None)


class RunnerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RunCount Fetcher")
        # self.setFixedSize(400, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Enter hardwaretyp:")
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("e.g., 10012345EX3456")
        self.btn_fetch = QPushButton("Fetch RunCount")
        self.result_label = QLabel("RunCount will appear here.")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.btn_fetch)
        self.layout.addWidget(self.result_label)

        self.btn_fetch.clicked.connect(self.start_thread)

    def start_thread(self):
        hardwaretyp = self.input_box.text().strip()
        if not hardwaretyp:
            QMessageBox.warning(self, "Input Error", "Please enter a valid hardwaretyp.")
            return

        self.thread = GetRunCount(hardwaretyp)
        self.thread.result_runcount.connect(self.display_result)
        self.thread.message_on_process.connect(self.update_status)
        self.thread.start()

    def update_status(self, msg):
        self.result_label.setText(msg)

    def display_result(self, result):
        if result is None:
            self.result_label.setText("❌ Failed to fetch run count.")
        else:
            self.result_label.setText(f"✅ RunCount: {result}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RunnerApp()
    window.show()
    sys.exit(app.exec())
