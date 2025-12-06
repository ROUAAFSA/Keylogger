import os
import socket
import sys
import datetime
import threading
import json

# SERVER CONFIGURATION
SERVER_PORT = 9999
LOG_FILE = 'server-copy.txt'

# Configuration that will be sent to clients
CLIENT_CONFIG = {
    'send_interval': 20,  # Seconds between sends (CHANGE THIS!)
    'buffer_size': 1024,
    'retry_attempts': 3
}

def handle_config_request(client_socket, address):
    """Send configuration to client"""
    try:
        # Send config as JSON
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
        
        print(f'[{timestamp}] Received {total_bytes} bytes from {address[0]} and appended to {LOG_FILE}')
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        client_socket.close()

def handle_client(client_socket, address):
    """Determine what the client wants (config or upload)"""
    try:
        # First byte tells us what the client wants
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

# Main server
s = socket.socket()
s.bind(("0.0.0.0", SERVER_PORT))
s.listen(10)

print('='*60)
print(f'Server Started - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*60)
print(f'Listening on port: {SERVER_PORT}')
print(f'Log file: {LOG_FILE}')
print(f'\nClient Configuration:')
print(f'  - Send Interval: {CLIENT_CONFIG["send_interval"]} seconds')
print(f'  - Buffer Size: {CLIENT_CONFIG["buffer_size"]} bytes')
print('='*60)
print('\nWaiting for connections...\n')

while True:
    client_socket, address = s.accept()
    
    # Handle each client in a separate thread
    client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
    client_thread.start()