"""Serializers for this API group."""
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core import messages as msg
from hotel_app.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - read/list operations."""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating User."""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=6,
        required=False,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']

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


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating User."""
    password = serializers.CharField(required=False, write_only=True, min_length=6)
    password_confirm = serializers.CharField(
        required=False,
        write_only=True,
        min_length=6,
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'role', 'is_active']

    def validate(self, data):
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise serializers.ValidationError(
                    {'password': msg.PASSWORDS_NOT_MATCH}
                )
        elif 'password' in data and 'password_confirm' not in data:
            raise serializers.ValidationError(
                {'password_confirm': msg.PASSWORD_CONFIRM_REQUIRED}
            )
        return data

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(msg.EMAIL_EXISTS)
        return value

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data.pop('password')
            )
        validated_data.pop('password_confirm', None)
        return super().update(instance, validated_data)
