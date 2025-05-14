import os
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from PIL import Image
from django.conf import settings


class UploadPhotoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('photo')
        if not image_file:
            return Response({'detail': 'No photo uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save original image
        filename = default_storage.save(f"photos/{image_file.name}", image_file)
        original_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Process image (convert to black and white)
        processed_filename = f"processed_{image_file.name}"
        processed_path = os.path.join(settings.MEDIA_ROOT, f"photos/{processed_filename}")
        
        with Image.open(original_path).convert("L") as img_bw:
            img_bw.save(processed_path)

        processed_url = settings.MEDIA_URL + f"photos/{processed_filename}"
        return Response({'processed_url': request.build_absolute_uri(processed_url)}, status=status.HTTP_201_CREATED)
