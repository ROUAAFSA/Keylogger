# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import socket
import datetime
import os

# Your original UI class (keep it as is)
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(399, 402)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName("mainLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tabServer = QtWidgets.QWidget()
        self.tabServer.setObjectName("tabServer")
        self.sessionFrame = QtWidgets.QFrame(self.tabServer)
        self.sessionFrame.setGeometry(QtCore.QRect(10, 250, 221, 37))
        self.sessionFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sessionFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sessionFrame.setObjectName("sessionFrame")
        self.sessionLayout = QtWidgets.QVBoxLayout(self.sessionFrame)
        self.sessionLayout.setObjectName("sessionLayout")
        self.labelUptime = QtWidgets.QLabel(self.sessionFrame)
        self.labelUptime.setObjectName("labelUptime")
        self.sessionLayout.addWidget(self.labelUptime)
        self.uptimeFrame = QtWidgets.QFrame(self.tabServer)
        self.uptimeFrame.setGeometry(QtCore.QRect(10, 190, 116, 37))
        self.uptimeFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.uptimeFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.uptimeFrame.setObjectName("uptimeFrame")
        self.uptimeLayout = QtWidgets.QVBoxLayout(self.uptimeFrame)
        self.uptimeLayout.setObjectName("uptimeLayout")
        self.labelSession = QtWidgets.QLabel(self.uptimeFrame)
        self.labelSession.setObjectName("labelSession")
        self.uptimeLayout.addWidget(self.labelSession)
        self.label_2 = QtWidgets.QLabel(self.tabServer)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 101, 16))
        self.label_2.setObjectName("label_2")
        self.line_2 = QtWidgets.QFrame(self.tabServer)
        self.line_2.setGeometry(QtCore.QRect(10, 30, 361, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.label_3 = QtWidgets.QLabel(self.tabServer)
        self.label_3.setGeometry(QtCore.QRect(20, 50, 341, 111))
        self.label_3.setObjectName("label_3")
        self.line_3 = QtWidgets.QFrame(self.tabServer)
        self.line_3.setGeometry(QtCore.QRect(10, 170, 361, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QtWidgets.QFrame(self.tabServer)
        self.line_4.setGeometry(QtCore.QRect(10, 230, 361, 20))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.tabServer)
        self.line_5.setGeometry(QtCore.QRect(10, 290, 361, 20))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.widget = QtWidgets.QWidget(self.tabServer)
        self.widget.setGeometry(QtCore.QRect(10, 320, 361, 31))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnStop = QtWidgets.QPushButton(self.widget)
        self.btnStop.setObjectName("btnStop")
        self.horizontalLayout.addWidget(self.btnStop)
        self.btnStart = QtWidgets.QPushButton(self.widget)
        self.btnStart.setObjectName("btnStart")
        self.horizontalLayout.addWidget(self.btnStart)
        self.btnSettings = QtWidgets.QPushButton(self.widget)
        self.btnSettings.setObjectName("btnSettings")
        self.horizontalLayout.addWidget(self.btnSettings)
        self.tabWidget.addTab(self.tabServer, "")
        self.tabLogs = QtWidgets.QWidget()
        self.tabLogs.setObjectName("tabLogs")
        self.scrollArea = QtWidgets.QScrollArea(self.tabLogs)
        self.scrollArea.setGeometry(QtCore.QRect(10, 50, 361, 251))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 359, 249))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.listView = QtWidgets.QListView(self.scrollAreaWidgetContents)
        self.listView.setGeometry(QtCore.QRect(0, 0, 371, 251))
        self.listView.setObjectName("listView")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label = QtWidgets.QLabel(self.tabLogs)
        self.label.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label.setObjectName("label")
        self.line = QtWidgets.QFrame(self.tabLogs)
        self.line.setGeometry(QtCore.QRect(10, 30, 361, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_6 = QtWidgets.QFrame(self.tabLogs)
        self.line_6.setGeometry(QtCore.QRect(10, 300, 361, 20))
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.widget1 = QtWidgets.QWidget(self.tabLogs)
        self.widget1.setGeometry(QtCore.QRect(10, 320, 361, 31))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnExportLogs = QtWidgets.QPushButton(self.widget1)
        self.btnExportLogs.setObjectName("btnExportLogs")
        self.horizontalLayout_2.addWidget(self.btnExportLogs)
        self.btnEncryptLogs = QtWidgets.QPushButton(self.widget1)
        self.btnEncryptLogs.setObjectName("btnEncryptLogs")
        self.horizontalLayout_2.addWidget(self.btnEncryptLogs)
        self.btnDeleteLogs = QtWidgets.QPushButton(self.widget1)
        self.btnDeleteLogs.setObjectName("btnDeleteLogs")
        self.horizontalLayout_2.addWidget(self.btnDeleteLogs)
        self.tabWidget.addTab(self.tabLogs, "")
        self.mainLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Modern Server Manager"))
        self.labelUptime.setStyleSheet(_translate("MainWindow", "font-size: 14px;"))
        self.labelUptime.setText(_translate("MainWindow", "Server Uptime: "))
        self.labelSession.setStyleSheet(_translate("MainWindow", "font-size: 14px;"))
        self.labelSession.setText(_translate("MainWindow", "Session ID: "))
        self.label_2.setText(_translate("MainWindow", "Server Status"))
        self.label_3.setText(_translate("MainWindow", "Status: Stopped\n\nReady to start server..."))
        self.btnStop.setText(_translate("MainWindow", "⏹ Stop Server"))
        self.btnStart.setText(_translate("MainWindow", "▶ Start Server"))
        self.btnSettings.setText(_translate("MainWindow", "⚙ Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabServer), _translate("MainWindow", "Server"))
        self.label.setText(_translate("MainWindow", "Received Logs"))
        self.btnExportLogs.setText(_translate("MainWindow", "📤 Export Logs"))
        self.btnEncryptLogs.setText(_translate("MainWindow", "🔐 Encrypt Logs"))
        self.btnDeleteLogs.setText(_translate("MainWindow", "🗑 Delete Logs"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLogs), _translate("MainWindow", "Logs"))


# SERVER THREAD - Runs in background
class ServerThread(QThread):
    status_update = pyqtSignal(str)  # Signal to send status updates
    log_received = pyqtSignal(str)   # Signal when log file is received
    
    def __init__(self, port=9999):
        super().__init__()
        self.port = port
        self.running = False
        self.server_socket = None
        
    def run(self):
        self.running = True
        try:
            self.server_socket = socket.socket()
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(10)
            self.server_socket.settimeout(1.0)  # Timeout so we can check if we should stop
            
            self.status_update.emit(f"Server listening on port {self.port}")
            
            while self.running:
                try:
                    sc, address = self.server_socket.accept()
                    self.status_update.emit(f"Connection from: {address[0]}:{address[1]}")
                    
                    # Receive file
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"received_log_{timestamp}.txt"
                    
                    with open(filename, 'wb') as f:
                        while True:
                            data = sc.recv(1024)
                            if not data:
                                break
                            f.write(data)
                    
                    sc.close()
                    self.status_update.emit(f"Log saved: {filename}")
                    self.log_received.emit(filename)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.status_update.emit(f"Error: {e}")
                        
        except Exception as e:
            self.status_update.emit(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            self.status_update.emit("Server stopped")
    
    def stop(self):
        self.running = False


# MAIN WINDOW - Connects UI to functionality
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Server variables
        self.server_thread = None
        self.start_time = None
        self.session_id = None
        self.log_files = []
        
        # Connect buttons to functions
        self.ui.btnStart.clicked.connect(self.start_server)
        self.ui.btnStop.clicked.connect(self.stop_server)
        self.ui.btnSettings.clicked.connect(self.open_settings)
        self.ui.btnExportLogs.clicked.connect(self.export_logs)
        self.ui.btnDeleteLogs.clicked.connect(self.delete_logs)
        self.ui.btnEncryptLogs.clicked.connect(self.encrypt_logs)
        
        # Timer for uptime
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_uptime)
        
        # Initial state
        self.ui.btnStop.setEnabled(False)
        
        # Setup log list model
        self.log_model = QtGui.QStandardItemModel()
        self.ui.listView.setModel(self.log_model)
        
    def start_server(self):
        """Start the server"""
        if self.server_thread is None or not self.server_thread.isRunning():
            # Generate session ID
            self.session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            self.start_time = datetime.datetime.now()
            
            # Update UI
            self.ui.labelSession.setText(f"Session ID: {self.session_id}")
            self.ui.label_3.setText("Status: Running\n\nServer is active and waiting for connections...")
            self.ui.btnStart.setEnabled(False)
            self.ui.btnStop.setEnabled(True)
            
            # Start server thread
            self.server_thread = ServerThread(port=9999)
            self.server_thread.status_update.connect(self.update_status)
            self.server_thread.log_received.connect(self.add_log_to_list)
            self.server_thread.start()
            
            # Start uptime timer
            self.timer.start(1000)  # Update every second
    
    def stop_server(self):
        """Stop the server"""
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop()
            self.server_thread.wait()
            
            # Update UI
            self.ui.label_3.setText("Status: Stopped\n\nServer has been stopped.")
            self.ui.btnStart.setEnabled(True)
            self.ui.btnStop.setEnabled(False)
            
            # Stop timer
            self.timer.stop()
    
    def update_status(self, message):
        """Update status label with server messages"""
        current_text = self.ui.label_3.text()
        lines = current_text.split('\n')
        
        # Keep first 2 lines (Status header), add new message
        new_text = '\n'.join(lines[:2]) + f"\n\n{message}"
        self.ui.label_3.setText(new_text)
    
    def update_uptime(self):
        """Update the uptime display"""
        if self.start_time:
            elapsed = datetime.datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.ui.labelUptime.setText(f"Server Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def add_log_to_list(self, filename):
        """Add received log file to the list"""
        self.log_files.append(filename)
        item = QtGui.QStandardItem(filename)
        self.log_model.appendRow(item)
    
    def export_logs(self):
        """Export all logs to a zip file"""
        if not self.log_files:
            QtWidgets.QMessageBox.information(self, "No Logs", "No logs to export!")
            return
        
        QtWidgets.QMessageBox.information(self, "Export", f"Exporting {len(self.log_files)} log files...")
    
    def delete_logs(self):
        """Delete all log files"""
        if not self.log_files:
            QtWidgets.QMessageBox.information(self, "No Logs", "No logs to delete!")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self, "Delete Logs", 
            f"Delete all {len(self.log_files)} log files?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            for log_file in self.log_files:
                try:
                    if os.path.exists(log_file):
                        os.remove(log_file)
                except Exception as e:
                    print(f"Error deleting {log_file}: {e}")
            
            self.log_files.clear()
            self.log_model.clear()
            QtWidgets.QMessageBox.information(self, "Success", "All logs deleted!")
    
    def encrypt_logs(self):
        """Encrypt log files"""
        if not self.log_files:
            QtWidgets.QMessageBox.information(self, "No Logs", "No logs to encrypt!")
            return
        
        QtWidgets.QMessageBox.information(self, "Encrypt", "Encryption feature coming soon!")
    
    def open_settings(self):
        """Open settings dialog"""
        QtWidgets.QMessageBox.information(self, "Settings", "Settings dialog coming soon!")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())