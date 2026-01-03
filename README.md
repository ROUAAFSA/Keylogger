# Keylogger Server System

A client-server keylogger system with real-time monitoring and secure log management capabilities.

## Overview

This project implements a comprehensive keylogger system consisting of:
- **Server**: Centralized logging server with GUI management interface
- **Client/Keylogger**: Keystroke capture agent with automatic log transmission
- **Utilities**: Log encryption, export, and analysis tools

### Key Features

- Real-time keystroke capture with UTF-8 support
- Centralized server with PyQt6 GUI interface
- Automatic log transmission at configurable intervals
- Connection tracking and statistics
- Log encryption with password protection
- Multiple export formats (TXT, CSV, JSON)
- Session management and device identification

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Operating system: Windows, Linux, or macOS

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd python_project
   ```

2. **Install Python dependencies**

   **For Linux/macOS (Virtual Environment - Recommended):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # Linux/macOS
   
   # Install dependencies
   pip install -r requirements.txt
   ```

   **For Kali Linux (System Packages):**
   ```bash
   sudo apt install python3-pyqt6 python3-pynput python3-pycryptodome
   ```

   **For Windows:**
   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
   - PyQt6 (GUI interface)
   - pynput (keyboard monitoring)
   - pycryptodome (log encryption)
   - pyinstaller (for building executables)

3. **Configure settings** (optional)
   
   Edit `settings.json` to customize:
   - Server port (default: 9999)
   - Log file path
   - Send interval (seconds)
   - Auto-stop timeout

## Usage

### Starting the Server

**Option 1: GUI Interface (Recommended)**
```bash
python interface.py
```

The GUI provides:
- Start/Stop server controls
- Real-time connection monitoring
- Live log viewing
- Export and encryption tools
- Configuration management

**Option 2: Command-Line Server**
```bash
python server.py
```

### Running the Keylogger Client

#### Method 1: Python Script (All Platforms)

On the target machine:
```bash
python keylogger.py
```

The client will:
1. Connect to the server to fetch configuration
2. Start capturing keystrokes
3. Automatically send logs at the configured interval
4. Press ESC to stop manually

#### Method 2: Windows Executable (Optional)

For easier deployment on Windows without Python installation:

1. **Configure the server IP** in `exe/client.py`:
   ```python
   SERVER_IP = "localhost"  # Change to your server's IP
   SERVER_PORT = 9999
   ```

2. **Build the executable** (one-time, after changing client.py):
   ```bash
   cd exe
   pip install pyinstaller  # If not already installed
   python -m PyInstaller --onefile --noconsole keylogger.py
   ```

3. **Run the executable**:
   - Navigate to `exe/dist/` folder
   - Double-click `keylogger.exe`
   - Press ESC to stop

**Note**: Windows Defender may flag the executable. Add an exception if needed.

### Configuration

Edit `client.py` (or `exe/client.py` for executable) to set:
- `SERVER_IP`: IP address of the server (default: localhost)
- `SERVER_PORT`: Server port (default: 9999)

**Example configurations:**
- Same machine: `SERVER_IP = "localhost"`
- Local network: `SERVER_IP = "192.168.1.100"`
- Remote server: `SERVER_IP = "203.0.113.5"`

### Log Management

**Export Logs**
- Use the GUI's "Export Logs" button
- Supports TXT, CSV, and JSON formats

**Encrypt Logs**
- Use the GUI's "Encrypt Logs" button
- Enter a strong password (minimum 4 characters)
- Encrypted files are saved with `.enc` extension

**Decrypt Logs**
```bash
python decrypt_logs.py
```

## File Structure

```
python_project/
├── exe/                      # Windows executable build
│   ├── dist/
│   │   └── keylogger.exe    # Built executable (after pyinstaller)
│   ├── build/               # Build artifacts
│   ├── keylogger.py         # Client source for exe
│   ├── client.py            # Client config for exe
│   └── keylogger.spec       # PyInstaller spec file
├── server.py                 # Main server (command-line)
├── interface.py              # GUI server manager
├── keylogger.py              # Keystroke capture client
├── client.py                 # Client network communication
├── settings.py               # GUI settings configuration
├── utils.py                  # Utility functions
├── decrypt_logs.py           # Log decryption tool
├── requirements.txt          # Python dependencies
└── settings.json             # Configuration file
```

## Technical Details

**Server Architecture**
- Multi-threaded socket server
- Handles three request types: Config (C), Log upload (L), Statistics (S)
- Connection tracking with automatic cleanup
- JSON-based configuration exchange

**Client Architecture**
- Keyboard listener using pynput
- Automatic reconnection on failure
- Device identification (username@hostname_OS)
- Configurable send intervals

**Log Format**
- JSON-structured entries: `[device_id, timestamp, message]`
- UTF-8 encoding for international characters
- Session markers for tracking

## Troubleshooting

### Linux Virtual Environment Issues

**Problem**: "externally-managed-environment" error on Kali/Debian

**Solution**: Use a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Connection Issues

**Problem**: Client can't connect to server

**Solutions**:
1. Check server IP in `client.py` matches server's actual IP
2. Verify firewall allows port 9999
3. Test connection: `telnet <server-ip> 9999`

### Windows Defender Alerts

**Problem**: Windows Defender flags `keylogger.exe`

**Solution**: Add exclusion in Windows Security → Virus & threat protection → Exclusions

##  ETHICAL WARNING

### Legal and Ethical Considerations

**THIS SOFTWARE IS FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY.**

Using keyloggers without explicit consent is:
- **ILLEGAL** in most jurisdictions
- A violation of privacy rights
- Subject to criminal prosecution
- Unethical and harmful

### Appropriate Use Cases

 **LEGAL USES:**
- Personal device monitoring with owner consent
- Parental control on children's devices (with appropriate age and notification)
- Corporate security monitoring with employee notification and consent
- Security research in controlled environments
- Educational demonstrations with explicit participant consent

 **ILLEGAL USES:**
- Monitoring others without their knowledge or consent
- Stealing passwords or personal information
- Workplace surveillance without proper disclosure
- Stalking or harassment
- Any form of unauthorized access

### User Responsibilities

By using this software, you agree to:
1. Obtain explicit written consent from all monitored parties
2. Comply with all applicable laws and regulations
3. Use the software only for legitimate, authorized purposes
4. Accept full responsibility for your actions
5. Understand that unauthorized use may result in criminal prosecution

### Developer Disclaimer

The developers of this software:
- Provide this tool solely for educational purposes
- Do not condone or support illegal use
- Accept no liability for misuse of this software
- Encourage ethical and legal practices in cybersecurity

### Privacy Best Practices

If using this software legally:
- Clearly notify monitored users
- Obtain documented consent
- Implement strong access controls
- Encrypt all captured data
- Establish data retention policies
- Provide opt-out mechanisms where appropriate

**Remember: With great power comes great responsibility. Use this knowledge ethically.**

## License

This software is provided as-is for educational purposes. Users are solely responsible for compliance with all applicable laws and regulations.

---
