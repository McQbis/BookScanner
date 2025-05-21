from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from .models import EncryptedPhoto
from .utils import generate_signed_url, verify_signed_url, get_user_key


class UploadEncryptedPhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Upload a photo and store it encrypted using the user's unique key.
        
        Returns:
            - 201 Created: with signed URL and photo ID
            - 400 Bad Request: if no file is uploaded
        """
        uploaded_file = request.FILES.get('photo')
        if not uploaded_file:
            return Response({"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        fernet = get_user_key(request.user.id)
        encrypted_data = fernet.encrypt(uploaded_file.read())
        encrypted_file = ContentFile(encrypted_data)

        photo = EncryptedPhoto.objects.create(
            user=request.user,
            file=None,
            original_filename=uploaded_file.name,
        )

        filename = f"user_{request.user.id}_{photo.id}.enc"
        photo.file.save(filename, encrypted_file)
        photo.save()

        signed_url = generate_signed_url(photo.id)
        full_url = request.build_absolute_uri(signed_url)

        return Response({
            "processed_url": full_url,
            "photo_id": photo.id,
        }, status=status.HTTP_201_CREATED)


class ViewDecryptedPhoto(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, photo_id):
        """
        Decrypt and return a specific photo owned by the authenticated user.

        This endpoint is useful for web applications or internal tools
        where authenticated users (or admins) need direct access to their
        decrypted images via secure, session- or token-based authentication.

        For mobile apps like React Native, using signed temporary URLs
        (see TemporaryDecryptedPhotoView) is more appropriate and efficient,
        especially for embedding images via URI.
        
        Returns:
            - 200 OK: FileResponse with decrypted image
            - 404 Not Found: if image is missing or decryption fails
        """
        photo = get_object_or_404(EncryptedPhoto, id=photo_id, user=request.user)
        fernet = get_user_key(request.user.id)

        try:
            with open(photo.file.path, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = fernet.decrypt(encrypted_data)
        except Exception:
            raise Http404("Could not decrypt the image.")

        return FileResponse(
            ContentFile(decrypted_data),
            content_type='image/jpeg',
            filename=photo.original_filename
        )


class TemporaryDecryptedPhotoView(APIView):
    """
    Serve a decrypted photo using a signed temporary URL.
    Does not require authentication.
    """
    permission_classes = []

    def get(self, request, signed_value):
        photo_id = verify_signed_url(signed_value)
        if photo_id is None:
            return HttpResponseForbidden("Invalid or expired link.")

        try:
            photo = EncryptedPhoto.objects.get(id=photo_id)
        except EncryptedPhoto.DoesNotExist:
            return HttpResponseNotFound("Photo not found.")

        fernet = get_user_key(photo.user.id)

        try:
            with open(photo.file.path, 'rb') as f:
                encrypted_data = f.read()
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
        """
        Delete a photo and remove the encrypted file from storage.
        
        Returns:
            - 204 No Content: if deletion is successful
            - 404 Not Found: if the photo does not exist or user is unauthorized
        """
        photo = get_object_or_404(EncryptedPhoto, id=photo_id, user=request.user)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListUserPhotosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List all encrypted photos for the authenticated user with temporary view links.
        
        Returns:
            - 200 OK: A list of photo metadata and signed URLs
        """
        user_photos = EncryptedPhoto.objects.filter(user=request.user)
        photo_list = []

        for photo in user_photos:
            signed_url = generate_signed_url(photo.id)
            full_url = request.build_absolute_uri(signed_url)
            photo_list.append({
                "photo_id": photo.id,
                "original_filename": photo.original_filename,
                "processed_url": full_url,
            })

        return Response(photo_list, status=status.HTTP_200_OK)