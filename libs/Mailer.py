import win32com.client as win32
from PyQt6.QtCore import QThread, pyqtSignal
from libs.DatabaseConnector import DatabaseConnector


class MailerThread(QThread):
    """
    Threaded mail sender to prevent blocking the GUI.
    Emits a signal when mailing is finished.
    """
    finish_mail = pyqtSignal(str)

    def __init__(self, message: str, function: str, subject: str, parent=None):
        super().__init__(parent)
        self.mailer = Mailer()
        self.message = message
        self.function = function
        self.subject = subject

    def run(self) -> None:
        try:
            self.mailer.history_mail(self.message, self.function, self.subject)
            self.finish_mail.emit("✅ Mail Sent Successfully.")
        except Exception as e:
            self.finish_mail.emit(f"❌ Mail Failed: {str(e)}")


class Mailer:
    """
    Handles the construction and sending of emails using Outlook.
    """
    def __init__(self) -> None:
        self.database = DatabaseConnector()

    def history_mail(self, message: str, function: str, subj: str) -> None:
        try:
            recipients = self.get_cc_to()

            # Check and parse recipient data
            if not recipients or len(recipients) < 2:
                raise ValueError("Recipient list must include both CC and To fields.")

            cc_recipients = recipients[0][1]
            to_recipients = recipients[1][1]

            if not cc_recipients or not to_recipients:
                raise ValueError("CC or To field is empty.")

            # Create Outlook email
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.Subject = subj
            mail.Body = message
            mail.To = to_recipients
            mail.CC = cc_recipients

            # Validate recipients
            if not mail.Recipients.ResolveAll():
                unresolved = [r.Name for r in mail.Recipients if not r.Resolved]
                raise Exception(f"Unresolved recipient(s): {unresolved}")

            # Send or Display mail
            if function.lower() == 'history':
                mail.Send()
            else:
                mail.Display()

        except Exception as e:
            raise Exception(f"Failed to send email: {e}")

    def get_cc_to(self) -> list:
        """
        Retrieves recipient information from the database.
        Returns:
            List[Tuple[str, str]]: Each tuple contains ('Type', 'email@example.com')
        """
        data = self.database.get_recepients()
        print("📨 Recipient data fetched from database:", data)
        return data

# if __name__ == "__main__":
#     from PyQt6.QtWidgets import (
#         QApplication, QWidget, QVBoxLayout,
#         QPushButton, QTextEdit, QLineEdit, QLabel, QMessageBox
#     )
#     from PyQt6.QtCore import Qt
#     import sys

#     class EmailSender(QWidget):
#         def __init__(self):
#             super().__init__()
#             self.setWindowTitle("Send Outlook Email")
#             self.setMinimumSize(400, 300)
#             self.setup_ui()

#         def setup_ui(self):
#             layout = QVBoxLayout()

#             self.subject_input = QLineEdit()
#             self.subject_input.setPlaceholderText("Enter Subject")

#             self.body_input = QTextEdit()
#             self.body_input.setPlaceholderText("Enter Message Body")

#             self.send_button = QPushButton("Send Email")
#             self.send_button.clicked.connect(self.send_email)

#             self.status_label = QLabel("")
#             self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

#             layout.addWidget(self.subject_input)
#             layout.addWidget(self.body_input)
#             layout.addWidget(self.send_button)
#             layout.addWidget(self.status_label)

#             self.setLayout(layout)

#         def send_email(self):
#             subject = self.subject_input.text().strip()
#             message = self.body_input.toPlainText().strip()

#             if not subject or not message:
#                 QMessageBox.warning(self, "Input Error", "Subject and Message must not be empty.")
#                 return

#             self.send_button.setEnabled(False)
#             self.status_label.setText("Sending email...")

#             self.thread = MailerThread(message, "history", subject)
#             self.thread.finish_mail.connect(self.on_mail_sent)
#             self.thread.start()

#         def on_mail_sent(self, result: str):
#             self.status_label.setText(result)
#             self.send_button.setEnabled(True)
#             QMessageBox.information(self, "Email Result", result)

#     app = QApplication(sys.argv)
#     window = EmailSender()
#     window.show()
#     sys.exit(app.exec())
