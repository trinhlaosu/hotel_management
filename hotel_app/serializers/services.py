"""Serializers for this API group."""
from rest_framework import serializers

from core import messages as msg
from hotel_app.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model."""
    price = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'price', 'description', 'is_active', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Service."""
    price = serializers.DecimalField(max_digits=15, decimal_places=0)

    class Meta:
        model = Service
        fields = ['name', 'price', 'description']

    def validate_name(self, value):
        if Service.objects.filter(name=value).exists():
            raise serializers.ValidationError(msg.SERVICE_NAME_EXISTS)
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(msg.PRICE_NON_NEGATIVE)
        return value


class ServiceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Service."""
    price = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        required=False,
    )

    class Meta:
        model = Service
        fields = ['name', 'price', 'description', 'is_active']

    def validate_name(self, value):
        service = self.instance
        if service is None:
            return value
        if Service.objects.exclude(pk=service.pk).filter(name=value).exists():
            raise serializers.ValidationError(msg.SERVICE_NAME_EXISTS)
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(msg.PRICE_NON_NEGATIVE)
        return value
