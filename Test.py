import sys
import time
from PyQt5 import QtWidgets, QtCore, QtGui

class ServerManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Server Manager")
        self.setGeometry(100, 100, 750, 520)

        # ---------------- Dark theme and style ----------------
        self.setStyleSheet("""
            QMainWindow { background-color: #2e2e2e; }
            QTabWidget::pane { border: 1px solid #444; background: #2e2e2e; }
            QTabBar::tab {
                background: #3c3f41; color: #ffffff; padding: 8px 20px;
                border-top-left-radius: 4px; border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { background: #565656; }
            QPushButton {
                border-radius: 8px; font-size: 16px; color: #fff;
            }
            QPushButton#btn_start { background-color: #28a745; }
            QPushButton#btn_stop { background-color: #dc3545; }
            QPushButton#btn_settings { background-color: #007bff; }
            QPushButton:hover { background-color: #666666; }
            QLabel { color: #ffffff; font-size: 14px; }
            QTextEdit {
                background-color: #1e1e1e; color: #dcdcdc; border: 1px solid #444;
                border-radius: 4px; font-family: Consolas; font-size: 13px;
            }
            QFrame { background-color: #3c3f41; border-radius: 4px; }
        """)

        # ---------------- Tab Widget ----------------
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setGeometry(10, 10, 720, 480)

        # ---------------- Tab 1: Server ----------------
        self.tab_server = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_server, "Server")

        # Compact info bar
        self.infoBar = QtWidgets.QFrame(self.tab_server)
        self.infoBar.setGeometry(10, 10, 690, 50)
        self.infoBar.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.label_session = QtWidgets.QLabel("Session ID:", self.infoBar)
        self.label_session.setGeometry(10, 10, 150, 30)
        self.value_session = QtWidgets.QLabel("SESSION-12345", self.infoBar)
        self.value_session.setGeometry(120, 10, 200, 30)
        self.value_session.setStyleSheet("color: #ffc107; font-weight: bold;")

        self.label_uptime = QtWidgets.QLabel("Server Uptime:", self.infoBar)
        self.label_uptime.setGeometry(350, 10, 120, 30)
        self.value_uptime = QtWidgets.QLabel("00:00:00", self.infoBar)
        self.value_uptime.setGeometry(470, 10, 200, 30)
        self.value_uptime.setStyleSheet("color: #17a2b8; font-weight: bold;")

        # Buttons
        self.btn_start = QtWidgets.QPushButton("Start Server", self.tab_server)
        self.btn_start.setGeometry(200, 90, 300, 60)
        self.btn_start.setObjectName("btn_start")

        self.btn_stop = QtWidgets.QPushButton("Stop Server", self.tab_server)
        self.btn_stop.setGeometry(200, 170, 300, 60)
        self.btn_stop.setObjectName("btn_stop")

        self.btn_settings = QtWidgets.QPushButton("Settings", self.tab_server)
        self.btn_settings.setGeometry(200, 250, 300, 60)
        self.btn_settings.setObjectName("btn_settings")

        # ---------------- Tab 2: Logs ----------------
        self.tab_logs = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_logs, "Logs")

        self.logViewer = QtWidgets.QTextEdit(self.tab_logs)
        self.logViewer.setGeometry(10, 10, 690, 350)
        self.logViewer.setReadOnly(True)

        self.btn_export = QtWidgets.QPushButton("Export Logs", self.tab_logs)
        self.btn_export.setGeometry(50, 380, 180, 40)
        self.btn_delete = QtWidgets.QPushButton("Delete Logs", self.tab_logs)
        self.btn_delete.setGeometry(270, 380, 180, 40)
        self.btn_encrypt = QtWidgets.QPushButton("Encrypt Logs", self.tab_logs)
        self.btn_encrypt.setGeometry(490, 380, 180, 40)

        # ---------------- Functionality ----------------
        self.server_start_time = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_uptime)
        self.timer.start(1000)

        self.btn_start.clicked.connect(self.start_server)
        self.btn_stop.clicked.connect(self.stop_server)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_export.clicked.connect(self.export_logs)
        self.btn_delete.clicked.connect(self.delete_logs)
        self.btn_encrypt.clicked.connect(self.encrypt_logs)

        self.log_counter = 0
        self.log_timer = QtCore.QTimer()
        self.log_timer.timeout.connect(self.add_log)
        self.log_timer.start(2000)  # Add a log every 2 seconds

    # ---------------- Methods ----------------
    def start_server(self):
        self.server_start_time = time.time()
        self.add_log("Server started.")

    def stop_server(self):
        self.add_log("Server stopped.")
        self.server_start_time = None
        self.value_uptime.setText("00:00:00")

    def open_settings(self):
        self.add_log("Settings clicked.")

    def export_logs(self):
        self.add_log("Logs exported.")

    def delete_logs(self):
        self.logViewer.clear()
        self.add_log("Logs deleted.")

    def encrypt_logs(self):
        self.add_log("Logs encrypted.")

    def update_uptime(self):
        if self.server_start_time:
            uptime = int(time.time() - self.server_start_time)
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.value_uptime.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self.value_uptime.setText("00:00:00")

    def add_log(self, *args):
        self.log_counter += 1
        timestamp = time.strftime("%H:%M:%S")
        # Alternate colors for better UI readability
        color = "#dcdcdc" if self.log_counter % 2 == 0 else "#a9a9a9"
        self.logViewer.append(f"<span style='color:{color}'>[{timestamp}] Example log message {self.log_counter}</span>")

# ---------------- Run App ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ServerManager()
    window.show()
    sys.exit(app.exec_())
