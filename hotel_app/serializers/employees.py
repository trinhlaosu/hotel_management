"""Serializers for this API group."""
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from core import messages as msg
from core.fields import NotFoundPrimaryKeyRelatedField
from hotel_app.models import Department, Employee, User


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    salary = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'phone', 'department', 'department_name',
            'shift', 'salary', 'status', 'username', 'email', 'hire_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Employee."""
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    department_id = NotFoundPrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        write_only=True,
    )
    salary = serializers.DecimalField(
        max_digits=15, decimal_places=0, required=False)

    class Meta:
        model = Employee
        fields = [
            'username', 'email', 'password', 'department_id', 'full_name',
            'phone', 'hire_date', 'salary', 'shift'
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(msg.USERNAME_EXISTS)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(msg.EMAIL_EXISTS)
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Create user first
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role='le_tan',
        )
        
        # Create employee
        employee = Employee.objects.create(user=user, **validated_data)
        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Employee."""
    department_id = NotFoundPrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        required=False,
        write_only=True,
    )
    salary = serializers.DecimalField(
        max_digits=15, decimal_places=0, required=False)

    class Meta:
        model = Employee
        fields = [
            'department_id', 'full_name', 'phone', 'salary', 'shift', 'status'
        ]
