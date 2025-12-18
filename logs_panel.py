# logs_panel.py
import os
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor

LOG_FILE = "server-copy.txt"

class LogsPanel(QTextEdit):
    def __init__(self, cards):
        super().__init__()
        self.cards = cards
        self.setReadOnly(True)
        self.last_size = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(2000)

    def update_logs(self):
        if not os.path.exists(LOG_FILE):
            return

        with open(LOG_FILE, "r") as f:
            text = f.read()

        # Update logs count
        self.cards.logs_count.setText(str(text.count("\n")))

        # Update only new logs
        new_text = text[self.last_size:]
        if new_text:
            at_bottom = self.verticalScrollBar().value() == self.verticalScrollBar().maximum()

            self.moveCursor(QTextCursor.MoveOperation.End)
            self.insertPlainText(new_text)

            if at_bottom:
                self.moveCursor(QTextCursor.MoveOperation.End)

            self.last_size = len(text)
