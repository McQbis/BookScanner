from django.db import models
from django.contrib.auth.models import User

class EncryptedPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='photos/', default='')
    original_filename = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)