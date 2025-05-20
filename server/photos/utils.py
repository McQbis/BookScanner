from cryptography.fernet import Fernet
from django.conf import settings
import os
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

def get_user_key(user_id):
    key_dir = os.path.join(settings.MEDIA_ROOT, 'keys')
    os.makedirs(key_dir, exist_ok=True)
    key_path = os.path.join(key_dir, f'user_{user_id}.key')

    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
    else:
        with open(key_path, 'rb') as f:
            key = f.read()
    
    return Fernet(key)



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