from rest_framework import serializers
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        """
        Validate that passwords match.
        Additional password strength checks can be added here.
        """
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({
                'password2': "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        """
        Create a new user with a securely hashed password.
        """
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )
        return user
