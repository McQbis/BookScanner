from django.urls import path
from .views import UploadEncryptedPhotoView, ViewDecryptedPhoto, TemporaryDecryptedPhotoView, DeletePhotoView

urlpatterns = [
    path('upload-photo/', UploadEncryptedPhotoView.as_view(), name='upload-photo'),
    path('view/<int:photo_id>/', ViewDecryptedPhoto.as_view(), name='view-photo'),
    path('temp-view/<str:signed_value>/', TemporaryDecryptedPhotoView.as_view()),
    path('delete-photo/<int:photo_id>/', DeletePhotoView.as_view(), name='delete-photo'),
]