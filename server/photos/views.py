from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import EncryptedPhoto
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
import tempfile
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from .utils import generate_signed_url, verify_signed_url, get_user_key

class UploadEncryptedPhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('photo')
        if not uploaded_file:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        fernet = get_user_key(request.user.id)
        encrypted = fernet.encrypt(uploaded_file.read())

        encrypted_file = ContentFile(encrypted)
        photo = EncryptedPhoto.objects.create(
            user=request.user,
            file=None,
            original_filename=uploaded_file.name,
        )
        filename = f'user_{request.user.id}_{photo.id}.enc'
        photo.file.save(filename, encrypted_file)
        photo.save()


        signed_url = generate_signed_url(photo.id)
        full_url = request.build_absolute_uri(signed_url)

        return Response({
            "processed_url": full_url,
            "photo_id": photo.id
        }, status=status.HTTP_201_CREATED)


class ViewDecryptedPhoto(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, photo_id):
        photo = get_object_or_404(EncryptedPhoto, id=photo_id, user=request.user)

        fernet = get_user_key(request.user.id)

        encrypted_path = photo.file.path
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = fernet.decrypt(encrypted_data)
        except Exception:
            raise Http404("Could not decrypt the image.")

        # Return decrypted image as response
        return FileResponse(
            ContentFile(decrypted_data),
            content_type='image/jpeg',  # or derive from original_filename
            filename=photo.original_filename
        )



class TemporaryDecryptedPhotoView(APIView):
    permission_classes = []  # No auth needed; URL is signed

    def get(self, request, signed_value):
        photo_id = verify_signed_url(signed_value)
        if photo_id is None:
            return HttpResponseForbidden("Invalid or expired link.")

        try:
            photo = EncryptedPhoto.objects.get(id=photo_id)
        except EncryptedPhoto.DoesNotExist:
            return HttpResponseNotFound("Photo not found.")

        fernet = get_user_key(photo.user.id)

        with open(photo.file.path, 'rb') as f:
            encrypted_data = f.read()
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
            except Exception:
                return HttpResponseForbidden("Could not decrypt the image.")

        return FileResponse(
            ContentFile(decrypted_data),
            content_type='image/jpeg',
            filename=photo.original_filename
        )
    
class DeletePhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, photo_id):
        photo = get_object_or_404(EncryptedPhoto, id=photo_id, user=request.user)
        photo.file.delete(save=False)  # delete file from storage
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListUserPhotosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_photos = EncryptedPhoto.objects.filter(user=request.user)
        photo_list = []

        for photo in user_photos:
            signed_url = generate_signed_url(photo.id)
            full_url = request.build_absolute_uri(signed_url)

            photo_list.append({
                "photo_id": photo.id,
                "processed_url": full_url,
                "original_filename": photo.original_filename,
            })

        return Response(photo_list)