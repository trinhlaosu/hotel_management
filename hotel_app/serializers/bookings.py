"""Serializers for this API group."""
from core import messages as msg
from core.fields import NotFoundPrimaryKeyRelatedField
from rest_framework import serializers

from hotel_app.models import Booking, BookingService, Customer, Room, Service


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'customer_name', 'room', 'room_number',
            'check_in', 'check_out', 'status', 'note', 'created_by',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Booking."""
    customer_id = NotFoundPrimaryKeyRelatedField(
        source='customer',
        queryset=Customer.objects.all(),
        write_only=True,
    )
    room_id = NotFoundPrimaryKeyRelatedField(
        source='room',
        queryset=Room.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Booking
        fields = ['customer_id', 'room_id', 'check_in', 'check_out', 'note']

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError(
                {'check_out': msg.CHECKOUT_AFTER_CHECKIN}
            )

        existing = Booking.objects.filter(
            room=data['room'],
            status__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_o'],
        ).exclude(is_deleted=True)

        if existing.filter(
            check_in__lt=data['check_out'],
            check_out__gt=data['check_in'],
        ).exists():
            raise serializers.ValidationError(
                {'room': msg.BOOKING_ROOM_UNAVAILABLE}
            )

        return data


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Booking."""
    class Meta:
        model = Booking
        fields = ['note']


class BookingServiceSerializer(serializers.ModelSerializer):
    """Serializer for BookingService model."""
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(
        source='service.price',
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
        read_only=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )

    class Meta:
        model = BookingService
        fields = [
            'id', 'booking', 'service', 'service_name', 'service_price',
            'quantity', 'subtotal', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating BookingService."""
    service_id = NotFoundPrimaryKeyRelatedField(
        source='service',
        queryset=Service.objects.all(),
        write_only=True,
    )

    class Meta:
        model = BookingService
        fields = ['service_id', 'quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(msg.SERVICE_QUANTITY_INVALID)
        return value


class BookingServiceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating BookingService."""
    class Meta:
        model = BookingService
        fields = ['quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(msg.SERVICE_QUANTITY_INVALID)
        return value
