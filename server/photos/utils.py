from cryptography.fernet import Fernet
from django.conf import settings
import os
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

master_fernet = Fernet(settings.MASTER_KEY.encode())

def get_user_key(user_id):
    key_dir = os.path.join(settings.MEDIA_ROOT, 'keys')
    os.makedirs(key_dir, exist_ok=True)

    key_path = os.path.join(key_dir, f'user_{user_id}.key')

    if not os.path.exists(key_path):
        # Generate a new user key
        user_key = Fernet.generate_key()
        encrypted_user_key = master_fernet.encrypt(user_key)

        with open(key_path, 'wb') as f:
            f.write(encrypted_user_key)
    else:
        with open(key_path, 'rb') as f:
            encrypted_user_key = f.read()

        try:
            user_key = master_fernet.decrypt(encrypted_user_key)
        except Exception as e:
            raise ValueError(f"Failed to decrypt key for user {user_id}: {e}")

    return Fernet(user_key)



signer = TimestampSigner()

def generate_signed_url(photo_id: int, max_age_seconds: int = 300) -> str:
    signed_value = signer.sign(str(photo_id))
    return f"/api/photos/temp-view/{signed_value}/"

def verify_signed_url(signed_value: str, max_age_seconds: int = 300) -> int:
    try:
        value = signer.unsign(signed_value, max_age=max_age_seconds)
        return int(value)
    except (BadSignature, SignatureExpired):
        return None