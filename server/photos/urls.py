from django.urls import path
from .views import UploadPhotoView

urlpatterns = [
    path('upload-photo/', UploadPhotoView.as_view(), name='upload-photo'),
]
