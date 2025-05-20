from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import os

from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        Validates the input and checks for email uniqueness.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            if User.objects.filter(email=email).exists():
                return Response(
                    {"detail": "A user with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.create_user(username=email, email=email, password=password)
            return Response(
                {"detail": "User registered successfully."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and return JWT tokens.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'email': user.email,
        })


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """
        Delete the authenticated user's account and their encrypted key file.
        """
        user = request.user
        key_path = os.path.join(settings.MEDIA_ROOT, 'keys', f'user_{user.id}.key')

        # Attempt to remove the encryption key file
        if os.path.exists(key_path):
            try:
                os.remove(key_path)
            except Exception as e:
                return Response(
                    {"detail": f"Failed to delete encryption key: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)