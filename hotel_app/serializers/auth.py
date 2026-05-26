"""Serializers for this API group."""
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from core import messages as msg
from hotel_app.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=6,
        required=False,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        password_confirm = data.get('password_confirm', data['password'])
        if data['password'] != password_confirm:
            raise serializers.ValidationError(
                {'password': msg.PASSWORDS_NOT_MATCH}
            )
        return data

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(msg.USERNAME_EXISTS)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(msg.EMAIL_EXISTS)
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating user profile."""
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        request = self.context.get('request')
        user = getattr(request, 'hotel_user', None)
        if user is None:
            return value
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(msg.EMAIL_EXISTS)
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    new_password_confirm = serializers.CharField(
        write_only=True,
        min_length=6,
        required=False,
    )

    def validate(self, data):
        new_password_confirm = data.get(
            'new_password_confirm',
            data['new_password'],
        )
        if data['new_password'] != new_password_confirm:
            raise serializers.ValidationError(
                {'new_password': msg.PASSWORDS_NOT_MATCH}
            )
        return data
