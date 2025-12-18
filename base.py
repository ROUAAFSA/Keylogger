# base.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from cards import StatusCards
from server_controls import ServerControls
from logs_panel import LogsPanel
from actions import ActionButtons

class KeyloggerDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keylogger Server Manager")
        self.setGeometry(100, 100, 900, 650)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Cards Section
        self.cards = StatusCards()
        layout.addLayout(self.cards)

        # Server Start/Stop Section
        self.server_controls = ServerControls(self.cards)
        layout.addLayout(self.server_controls)

        # Logs Panel
        self.logs_panel = LogsPanel(self.cards)
        layout.addWidget(self.logs_panel)

        # Export / Encrypt / Delete
        self.action_buttons = ActionButtons()
        layout.addLayout(self.action_buttons)

        # Dark mode theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 12px;
            }
            QPushButton {
                background-color: #444;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox:title {
                color: white;
                font-weight: bold;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyloggerDashboard()
    window.show()
    sys.exit(app.exec())
