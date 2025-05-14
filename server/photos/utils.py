from cryptography.fernet import Fernet
from django.conf import settings

ENCRYPTION_KEY = settings.ENCRYPTION_KEY.decode()

def encrypt_file(file_data: bytes) -> bytes:
    fernet = Fernet(ENCRYPTION_KEY)
    return fernet.encrypt(file_data)

def decrypt_file(file_data: bytes) -> bytes:
    fernet = Fernet(ENCRYPTION_KEY)
    return fernet.decrypt(file_data)