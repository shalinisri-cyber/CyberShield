import os
import base64
import hashlib

from cryptography.fernet import Fernet


def generate_key(password):
    password_hash = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(password_hash)


def encrypt_file(file_path, password):
    key = generate_key(password)
    cipher = Fernet(key)

    with open(file_path, "rb") as file:
        data = file.read()

    encrypted_data = cipher.encrypt(data)

    encrypted_path = file_path + ".encrypted"

    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)

    return encrypted_path


def decrypt_file(file_path, password):
    key = generate_key(password)
    cipher = Fernet(key)

    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    if file_path.endswith(".encrypted"):
        original_path = file_path[:-10]
    else:
        original_path = file_path + ".decrypted"

    with open(original_path, "wb") as file:
        file.write(decrypted_data)

    return original_path