import sys
import time
import random
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QObject, QTimer


def main():
    app = QApplication(sys.argv)

    loader = QUiLoader()
    window = loader.load("server_interface.ui")
    window.show()

    # -------------------------
    # GET WIDGETS
    # -------------------------
    btn_start = window.findChild(QObject, "btnStart")
    btn_stop = window.findChild(QObject, "btnStop")
    label_uptime = window.findChild(QObject, "labelUptime")
    label_session = window.findChild(QObject, "labelSession")

    # -------------------------
    # TIMER + STATE
    # -------------------------
    timer = QTimer()
    start_time = {"value": None}
    server_running = {"value": False}  # Track server state

    # -------------------------
    # INITIAL BUTTON STATES
    # -------------------------
    btn_start.setEnabled(True)
    btn_stop.setEnabled(False)

    # -------------------------
    # FUNCTIONS
    # -------------------------
    def update_uptime():
        if start_time["value"] is None:
            return

        elapsed = int(time.time() - start_time["value"])
        h = elapsed // 3600
        m = (elapsed % 3600) // 60
        s = elapsed % 60

        label_uptime.setText(f"Server Uptime: {h:02}:{m:02}:{s:02}")

    def start_button_clicked():
        if server_running["value"]:
            return  # Already running, ignore click

        print("Start button clicked")
        server_running["value"] = True

        # Disable Start, enable Stop
        btn_start.setEnabled(False)
        btn_stop.setEnabled(True)

        # Reset uptime
        start_time["value"] = time.time()
        update_uptime()
        timer.start(1000)

        # Random session ID
        session_id = random.randint(1000, 9999)
        label_session.setText(f"Session ID: {session_id}")

    def stop_button_clicked():
        if not server_running["value"]:
            return  # Already stopped, ignore click

        print("Stop button clicked")
        server_running["value"] = False

        # Enable Start, disable Stop
        btn_start.setEnabled(True)
        btn_stop.setEnabled(False)

        timer.stop()

    # -------------------------
    # CONNECT BUTTONS
    # -------------------------
    btn_start.clicked.connect(start_button_clicked)
    btn_stop.clicked.connect(stop_button_clicked)
    timer.timeout.connect(update_uptime)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
