import os
from cryptography.fernet import Fernet
import base64

# In a production environment, this key should be stored in environment variables or a secret manager.
# For this prototype, we generate it once or use a fixed one if not found.
SECRET_KEY_FILE = "secret.key"

def get_or_create_key():
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(SECRET_KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

FERNET_KEY = get_or_create_key()
cipher_suite = Fernet(FERNET_KEY)

def encrypt_data(data: str) -> str:
    if not data:
        return ""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception:
        return "[Decryption Error]"
