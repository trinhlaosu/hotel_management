"""Serializers for this API group."""
from rest_framework import serializers

from core import messages as msg
from core.fields import NotFoundPrimaryKeyRelatedField
from hotel_app.models import Booking, Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    booking_id = serializers.IntegerField(read_only=True)
    customer_name = serializers.CharField(
        source='booking.customer.full_name',
        read_only=True,
    )
    room_number = serializers.CharField(
        source='booking.room.room_number',
        read_only=True,
    )
    room_charge = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )
    service_charge = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )
    total = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )

    class Meta:
        model = Invoice
        fields = [
            'id', 'booking', 'booking_id', 'customer_name', 'room_number',
            'room_charge', 'service_charge', 'total', 'payment_status',
            'payment_method', 'paid_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Invoice."""
    booking_id = NotFoundPrimaryKeyRelatedField(
        source='booking',
        queryset=Booking.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Invoice
        fields = ['booking_id']


class InvoicePaySerializer(serializers.ModelSerializer):
    """Serializer for paying Invoice."""
    class Meta:
        model = Invoice
        fields = ['payment_method', 'paid_at']

    def validate_payment_method(self, value):
        if value not in dict(Invoice.PAYMENT_METHOD_CHOICES):
            raise serializers.ValidationError(msg.PAYMENT_METHOD_INVALID)
        return value
