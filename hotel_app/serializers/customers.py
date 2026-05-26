"""Serializers for this API group."""
from rest_framework import serializers

from core import messages as msg
from hotel_app.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'phone', 'email', 'id_card', 'address',
            'customer_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Customer."""
    class Meta:
        model = Customer
        fields = [
            'full_name', 'phone', 'id_card', 'email', 'address', 'customer_type'
        ]

    def validate_phone(self, value):
        if Customer.objects.filter(phone=value).exists():
            raise serializers.ValidationError(msg.CUSTOMER_PHONE_EXISTS)
        return value

    def validate_id_card(self, value):
        if Customer.objects.filter(id_card=value).exists():
            raise serializers.ValidationError(msg.CUSTOMER_ID_CARD_EXISTS)
        return value


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Customer."""
    class Meta:
        model = Customer
        fields = [
            'full_name', 'phone', 'id_card', 'email', 'address', 'customer_type'
        ]

    def validate_phone(self, value):
        customer = self.instance
        if Customer.objects.exclude(pk=customer.pk).filter(phone=value).exists():
            raise serializers.ValidationError(msg.CUSTOMER_PHONE_EXISTS)
        return value

    def validate_id_card(self, value):
        customer = self.instance
        if Customer.objects.exclude(pk=customer.pk).filter(id_card=value).exists():
            raise serializers.ValidationError(msg.CUSTOMER_ID_CARD_EXISTS)
        return value
