#!/usr/bin/env python3
"""
Decrypt Logs Script - Decrypts AES-256 encrypted log files
Usage command: python decrypt_logs.py encrypted_file.enc output_file.txt
"""

import sys
import getpass
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

def decrypt_logs(encrypted_file, password, output_file):
    """Decrypt log file with AES-256 using password"""
    try:
        # Read encrypted file (salt, nonce, tag, ciphertext)
        with open(encrypted_file, "rb") as f:
            salt = f.read(32)
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()
        
        print(f"Read encrypted file: {encrypted_file}")
        print(f"File size: {len(ciphertext) + 64} bytes")
        
        # Derive key from password using PBKDF2
        print("Deriving key from password...")
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        
        # Decrypt using AES-EAX mode
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        print("Decrypting...")
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        # Save decrypted file
        with open(output_file, "wb") as f:
            f.write(plaintext)
        
        print(f"Success! Decrypted file saved to: {output_file}")
        print(f"Decrypted size: {len(plaintext)} bytes")
        return True
        
    except ValueError:
        print("Error: Wrong password or corrupted file")
        return False
    except FileNotFoundError:
        print(f"Error: File not found: {encrypted_file}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("="*60)
    print("Keylogger - Decrypt Logs")
    print("="*60)
    
    if len(sys.argv) != 3:
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <encrypted_file> <output_file>")
        print("\nExample:")
        print(f"  python {sys.argv[0]} logs_encrypted_20251225_120000.enc logs_decrypted.txt")
        print()
        sys.exit(1)
    
    encrypted_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"\nEncrypted file: {encrypted_file}")
    print(f"Output file: {output_file}")
    print()
    
    password = getpass.getpass("Enter decryption password: ")
    
    if not password:
        print("Password cannot be empty")
        sys.exit(1)
    
    print()
    success = decrypt_logs(encrypted_file, password, output_file)
    print("="*60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()