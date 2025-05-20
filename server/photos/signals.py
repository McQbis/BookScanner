import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import EncryptedPhoto

@receiver(post_delete, sender=EncryptedPhoto)
def delete_photo_file(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        try:
            os.remove(instance.file.path)
        except Exception as e:
            print(f"Failed to delete file {instance.file.path}: {e}")