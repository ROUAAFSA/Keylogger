# cards.py
from PyQt6.QtWidgets import QLabel, QGridLayout, QGroupBox, QVBoxLayout

class StatusCards(QGridLayout):
    def __init__(self):
        super().__init__()

        # Server Status Card
        self.server_status = QLabel("Offline")
        self.uptime = QLabel("00:00:00")

        card1 = QGroupBox("Main Server")
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Port: 9999"))
        v1.addWidget(QLabel("Session ID: —"))
        v1.addWidget(QLabel("Uptime:"))
        v1.addWidget(self.uptime)
        v1.addWidget(self.server_status)
        card1.setLayout(v1)
        self.addWidget(card1, 0, 0)

        # Connections Card
        self.connections = QLabel("0")
        card2 = QGroupBox("Connections")
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Total Received:"))
        v2.addWidget(self.connections)
        card2.setLayout(v2)
        self.addWidget(card2, 0, 1)

        # Log Storage Card
        self.logs_count = QLabel("0")
        card3 = QGroupBox("Log Storage")
        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Total Logs:"))
        v3.addWidget(self.logs_count)
        card3.setLayout(v3)
        self.addWidget(card3, 0, 2)
