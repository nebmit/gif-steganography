import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _derive_key(passphrase: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return key


def _encrypt_message(message: str, passphrase: str):
    salt = os.urandom(16)
    key = _derive_key(passphrase, salt)
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return salt + encrypted_message


def _decrypt_message(encrypted_message_with_salt: bytes, passphrase: str):
    if len(encrypted_message_with_salt) < 16:
        raise InvalidToken("Invalid message")
    salt = encrypted_message_with_salt[:16]
    encrypted_message = encrypted_message_with_salt[16:]
    key = _derive_key(passphrase, salt)
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message).decode()
    return decrypted_message
