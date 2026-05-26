"""Serializers for this API group."""
from rest_framework import serializers

from core import messages as msg
from hotel_app.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Department."""
    class Meta:
        model = Department
        fields = ['name', 'description']

    def validate_name(self, value):
        if Department.objects.filter(name=value).exists():
            raise serializers.ValidationError(msg.DEPARTMENT_NAME_EXISTS)
        return value


class DepartmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Department."""
    class Meta:
        model = Department
        fields = ['name', 'description']

    def validate_name(self, value):
        department = self.instance
        if Department.objects.exclude(pk=department.pk).filter(name=value).exists():
            raise serializers.ValidationError(msg.DEPARTMENT_NAME_EXISTS)
        return value
