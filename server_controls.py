# server_controls.py
import subprocess
import datetime
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer

SERVER_SCRIPT = "server.py"
server_process = None

class ServerControls(QHBoxLayout):
    def __init__(self, cards):
        super().__init__()
        self.cards = cards
        self.server_running = False
        self.start_time = None

        # Buttons
        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)

        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_server)

        self.addWidget(self.start_btn)
        self.addWidget(self.stop_btn)

        # Uptime timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_uptime)
        self.timer.start(1000)

    def start_server(self):
        global server_process
        server_process = subprocess.Popen(["python", SERVER_SCRIPT])
        self.server_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.start_time = datetime.datetime.now()
        self.cards.server_status.setText("Online")

    def stop_server(self):
        global server_process
        if server_process:
            server_process.terminate()
            server_process = None

        self.server_running = False
        self.cards.server_status.setText("Offline")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_uptime(self):
        if self.server_running:
            elapsed = datetime.datetime.now() - self.start_time
            h, r = divmod(int(elapsed.total_seconds()), 3600)
            m, s = divmod(r, 60)
            self.cards.uptime.setText(f"{h:02}:{m:02}:{s:02}")
