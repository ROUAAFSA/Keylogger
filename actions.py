# actions.py
import os
import json
import csv
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QMessageBox

LOG_FILE = "server-copy.txt"
KEY = b"0123456789ABCDEF0123456789ABCDEF"  # 32 bytes for AES-256

class ActionButtons(QHBoxLayout):
    def __init__(self):
        super().__init__()

        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs)
        self.addWidget(export_btn)

        encrypt_btn = QPushButton("Encrypt Logs")
        encrypt_btn.clicked.connect(self.encrypt_logs)
        self.addWidget(encrypt_btn)

        delete_btn = QPushButton("Delete Logs")
        delete_btn.clicked.connect(self.delete_logs)
        self.addWidget(delete_btn)

    def export_logs(self):
        if not os.path.exists(LOG_FILE):
            return

        with open(LOG_FILE, "r") as f:
            lines = f.readlines()

        # Export JSON
        with open("logs.json", "w") as f:
            json.dump(lines, f, indent=2)

        # Export CSV
        with open("logs.csv", "w", newline="") as f:
            writer = csv.writer(f)
            for line in lines:
                writer.writerow([line.strip()])

        QMessageBox.information(None, "Export", "Logs exported as JSON and CSV")

    def encrypt_logs(self):
        try:
            from Crypto.Cipher import AES
        except:
            QMessageBox.warning(None, "Error", "PyCryptodome not installed!")
            return

        if not os.path.exists(LOG_FILE):
            return

        with open(LOG_FILE, "rb") as f:
            data = f.read()

        cipher = AES.new(KEY, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        with open("logs.enc", "wb") as f:
            f.write(cipher.nonce + ciphertext)

        QMessageBox.information(None, "Encrypt", "Logs encrypted -> logs.enc")

    def delete_logs(self):
        open(LOG_FILE, "w").close()
        QMessageBox.information(None, "Delete", "Logs cleared")
