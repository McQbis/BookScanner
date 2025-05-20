import os
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


# Initialize master encryption key
try:
    master_fernet = Fernet(settings.MASTER_KEY.encode())
except Exception as e:
    raise RuntimeError("Invalid MASTER_KEY in settings. Ensure it's a valid base64-encoded Fernet key.") from e


def get_user_key(user_id: int) -> Fernet:
    """
    Retrieves or generates a user-specific encryption key.
    The key is encrypted using the master key and stored on disk.
    
    Args:
        user_id (int): The user's ID.
    
    Returns:
        Fernet: A Fernet instance initialized with the user's decrypted key.
    
    Raises:
        ValueError: If the user's key cannot be decrypted.
    """
    key_dir = os.path.join(settings.MEDIA_ROOT, 'keys')
    os.makedirs(key_dir, exist_ok=True)

    key_path = os.path.join(key_dir, f"user_{user_id}.key")

    if not os.path.exists(key_path):
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
            raise ValueError(f"Failed to decrypt key for user {user_id}") from e

    return Fernet(user_key)


# Timestamp signer for generating and verifying temporary URLs
signer = TimestampSigner()


def generate_signed_url(photo_id: int, max_age_seconds: int = 300) -> str:
    """
    Creates a signed, time-limited URL for accessing a photo.

    Args:
        photo_id (int): The ID of the photo.
        max_age_seconds (int): URL expiration in seconds.

    Returns:
        str: Signed URL path.
    """
    signed_value = signer.sign(str(photo_id))
    return f"/api/photos/temp-view/{signed_value}/"


def verify_signed_url(signed_value: str, max_age_seconds: int = 300) -> int | None:
    """
    Verifies a signed URL value.

    Args:
        signed_value (str): The signed value from the URL.
        max_age_seconds (int): Max allowed age of the signature.

    Returns:
        int | None: The photo ID if valid; otherwise None.
    """
    try:
        value = signer.unsign(signed_value, max_age=max_age_seconds)
        return int(value)
    except (BadSignature, SignatureExpired):
        return None