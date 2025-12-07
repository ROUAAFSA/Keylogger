import os
import socket
import sys
import datetime
import threading
import json

# SERVER CONFIGURATION
SERVER_PORT = 9999
LOG_FILE = 'server-copy.txt'

# Configuration that will be sent to clients (YOU CAN CHANGE THIS ANYTIME!)
CLIENT_CONFIG = {
    'send_interval': 10,  # Seconds between sends
    'buffer_size': 1024,
    'retry_attempts': 3,
    'config_check_interval': 30  # How often clients check for config updates
}

# Lock for thread-safe config updates
config_lock = threading.Lock()

def update_config(new_interval):
    """Update the send interval (can be called from GUI or command line)"""
    global CLIENT_CONFIG
    with config_lock:
        CLIENT_CONFIG['send_interval'] = new_interval
        print(f"\n{'='*60}")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] CONFIG UPDATED!")
        print(f"New send interval: {new_interval} seconds")
        print(f"All clients will update on their next check")
        print(f"{'='*60}\n")

def handle_config_request(client_socket, address):
    """Send current configuration to client"""
    try:
        with config_lock:
            config_json = json.dumps(CLIENT_CONFIG)
        client_socket.send(config_json.encode('utf-8'))
        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Sent config to {address[0]}: interval={CLIENT_CONFIG["send_interval"]}s')
    except Exception as e:
        print(f'Error sending config: {e}')
    finally:
        client_socket.close()

def handle_log_upload(client_socket, address):
    """Receive logs from client"""
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
        
        print(f'[{timestamp}] Received {total_bytes} bytes from {address[0]}')
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        client_socket.close()

def handle_client(client_socket, address):
    """Determine what the client wants (config or upload)"""
    try:
        request_type = client_socket.recv(1).decode('utf-8')
        
        if request_type == 'C':  # Config request
            handle_config_request(client_socket, address)
        elif request_type == 'L':  # Log upload
            handle_log_upload(client_socket, address)
        else:
            print(f'Unknown request type from {address[0]}: {request_type}')
            client_socket.close()
            
    except Exception as e:
        print(f'Error handling client: {e}')
        client_socket.close()

def command_interface():
    """Command line interface to change settings while server runs"""
    print("\nCommand Interface Started (type 'help' for commands)\n")
    
    while True:
        try:
            cmd = input("server> ").strip().lower()
            
            if cmd == 'help':
                print("\nAvailable commands:")
                print("  interval <seconds>  - Set client send interval")
                print("  show                - Show current config")
                print("  quit                - Stop server")
                print()
                
            elif cmd.startswith('interval '):
                try:
                    new_interval = int(cmd.split()[1])
                    if new_interval < 5:
                        print("Error: Interval must be at least 5 seconds")
                    else:
                        update_config(new_interval)
                except (ValueError, IndexError):
                    print("Usage: interval <seconds>")
                    
            elif cmd == 'show':
                print(f"\nCurrent Configuration:")
                print(f"  Send Interval: {CLIENT_CONFIG['send_interval']} seconds")
                print(f"  Config Check Interval: {CLIENT_CONFIG['config_check_interval']} seconds")
                print(f"  Buffer Size: {CLIENT_CONFIG['buffer_size']} bytes")
                print()
                
            elif cmd == 'quit':
                print("Shutting down server...")
                os._exit(0)
                
            elif cmd == '':
                continue
                
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
                
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

# Main server
s = socket.socket()
s.bind(("0.0.0.0", SERVER_PORT))
s.listen(10)

print('='*60)
print(f'Server Started - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*60)
print(f'Listening on port: {SERVER_PORT}')
print(f'Log file: {LOG_FILE}')
print(f'\nInitial Client Configuration:')
print(f'  - Send Interval: {CLIENT_CONFIG["send_interval"]} seconds')
print(f'  - Config Check Interval: {CLIENT_CONFIG["config_check_interval"]} seconds')
print(f'  - Buffer Size: {CLIENT_CONFIG["buffer_size"]} bytes')
print('='*60)
print('\nType "help" for commands\n')

# Start command interface in separate thread
cmd_thread = threading.Thread(target=command_interface, daemon=True)
cmd_thread.start()

print('Waiting for connections...\n')

while True:
    try:
        client_socket, address = s.accept()
        
        # Handle each client in a separate thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        break