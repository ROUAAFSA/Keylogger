import os
import socket
import threading
import datetime
import json

SERVER_PORT = 9999
LOG_FILE = 'server-copy.txt'

# init config 
CLIENT_CONFIG = {
    'send_interval': 10, 
    'buffer_size': 1024,
    'retry_attempts': 3,
    'config_check_interval': 30
}

config_lock = threading.Lock()
server_running = True  # Global flag to control server loop

def update_config(new_interval):
    global CLIENT_CONFIG
    with config_lock:
        CLIENT_CONFIG['send_interval'] = new_interval
        print(f"\n{'='*60}")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] CONFIG UPDATED!")
        print(f"New send interval: {new_interval} seconds")
        print(f"{'='*60}\n")

def handle_config_request(client_socket, address):
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
    global server_running
    while server_running:
        try:
            cmd = input("server> ").strip().lower()
            if cmd == 'help':
                print("Available commands: interval <seconds>, show, quit")
            elif cmd.startswith('interval '):
                try:
                    new_interval = int(cmd.split()[1])
                    if new_interval < 5:
                        print("Interval must be >= 5s")
                    else:
                        update_config(new_interval)
                except:
                    print("Usage: interval <seconds>")
            elif cmd == 'show':
                print(CLIENT_CONFIG)
            elif cmd == 'quit':
                print("Shutting down server...")
                server_running = False
                break
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

# --- Main server ---
s = socket.socket()
s.bind(("0.0.0.0", SERVER_PORT))
s.listen(10)

print(f"Server started on port {SERVER_PORT}")
print(f"Log file: {LOG_FILE}")

cmd_thread = threading.Thread(target=command_interface, daemon=True)
cmd_thread.start()

try:
    while server_running:
        client_socket, address = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()
finally:
    s.close()
    print("Server socket closed")
