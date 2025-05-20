import os
import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import EncryptedPhoto

logger = logging.getLogger(__name__)

@receiver(post_delete, sender=EncryptedPhoto)
def delete_encrypted_photo_file(sender, instance, **kwargs):
    """
    Deletes the encrypted photo file from the filesystem when the EncryptedPhoto instance is deleted.
    """
    file_path = getattr(instance.file, 'path', None)

    if file_path and os.path.isfile(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}", exc_info=True)
