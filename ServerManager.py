import sys
import time
import random
import subprocess
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
    server_running = {"value": False}
    server_process = {"process": None}  # Store the server process

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

        print("▶ Starting server...")
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

        # Start server.py as a HIDDEN subprocess (no console window)
        try:
            # Use CREATE_NO_WINDOW to hide the console
            if sys.platform == 'win32':
                # Windows - hide console
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                server_process["process"] = subprocess.Popen(
                    [sys.executable, "server.py"],
                    startupinfo=startupinfo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
            else:
                # Linux/Mac
                server_process["process"] = subprocess.Popen(
                    [sys.executable, "server.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )
            
            print(f"✓ Server started (PID: {server_process['process'].pid})")
        except Exception as e:
            print(f"✗ Error starting server: {e}")
            # Revert UI state on error
            btn_start.setEnabled(True)
            btn_stop.setEnabled(False)
            server_running["value"] = False
            timer.stop()

    def stop_button_clicked():
        if not server_running["value"]:
            return  # Already stopped, ignore click

        print("⏹ Stopping server...")
        server_running["value"] = False

        # Stop the server process
        if server_process["process"]:
            try:
                # First try graceful termination
                server_process["process"].terminate()
                
                # Wait up to 5 seconds for process to end
                try:
                    server_process["process"].wait(timeout=5)
                    print("✓ Server stopped gracefully")
                except subprocess.TimeoutExpired:
                    # If still running after 5 seconds, force kill
                    server_process["process"].kill()
                    server_process["process"].wait()
                    print("✓ Server force-stopped")
                    
                server_process["process"] = None
                
            except Exception as e:
                print(f"⚠ Error stopping server: {e}")

        # Enable Start, disable Stop
        btn_start.setEnabled(True)
        btn_stop.setEnabled(False)

        # Stop timer
        timer.stop()

    # Cleanup when window closes
    def on_close(event):
        if server_running["value"] and server_process["process"]:
            print("Closing GUI, stopping server...")
            try:
                server_process["process"].terminate()
                server_process["process"].wait(timeout=3)
                print("✓ Server stopped")
            except subprocess.TimeoutExpired:
                server_process["process"].kill()
                print("✓ Server force-killed")
            except Exception as e:
                print(f"⚠ Error during cleanup: {e}")
        event.accept()

    # Override close event
    original_close = window.closeEvent
    def close_wrapper(event):
        on_close(event)
        if original_close:
            original_close(event)
    window.closeEvent = close_wrapper

    # -------------------------
    # CONNECT BUTTONS
    # -------------------------
    btn_start.clicked.connect(start_button_clicked)
    btn_stop.clicked.connect(stop_button_clicked)
    timer.timeout.connect(update_uptime)

    print("✓ GUI Ready. Click 'Start Server' to begin.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()