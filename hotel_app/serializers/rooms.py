"""Serializers for this API group."""
from rest_framework import serializers

from core import messages as msg
from core.fields import NotFoundPrimaryKeyRelatedField
from hotel_app.models import Room, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    """Serializer for RoomType model."""
    price_per_night = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
    )

    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'price_per_night', 'capacity', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomTypeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating RoomType."""
    price_per_night = serializers.DecimalField(max_digits=15, decimal_places=0)

    class Meta:
        model = RoomType
        fields = ['name', 'price_per_night', 'capacity', 'description']

    def validate_name(self, value):
        if RoomType.objects.filter(name=value).exists():
            raise serializers.ValidationError(msg.ROOM_TYPE_NAME_EXISTS)
        return value


class RoomTypeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating RoomType."""
    price_per_night = serializers.DecimalField(
        max_digits=15,
        decimal_places=0,
        required=False,
    )

    class Meta:
        model = RoomType
        fields = ['name', 'price_per_night', 'capacity', 'description']

    def validate_name(self, value):
        room_type = self.instance
        if room_type is None:
            return value
        if RoomType.objects.exclude(pk=room_type.pk).filter(name=value).exists():
            raise serializers.ValidationError(msg.ROOM_TYPE_NAME_EXISTS)
        return value


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model."""
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    price_per_night = serializers.DecimalField(
        source='room_type.price_per_night',
        max_digits=15,
        decimal_places=0,
        coerce_to_string=False,
        read_only=True,
    )
    capacity = serializers.IntegerField(source='room_type.capacity', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'floor', 'status', 'room_type',
            'room_type_name', 'price_per_night', 'capacity', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Room."""
    room_type_id = NotFoundPrimaryKeyRelatedField(
        source='room_type',
        queryset=RoomType.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Room
        fields = ['room_type_id', 'room_number', 'floor', 'status']

    def validate_room_number(self, value):
        if Room.objects.filter(room_number=value).exists():
            raise serializers.ValidationError(msg.ROOM_NUMBER_EXISTS)
        return value

    def validate(self, data):
        if data.get('status') and data['status'] not in dict(Room.STATUS_CHOICES):
            raise serializers.ValidationError(
                {'status': msg.ROOM_STATUS_INVALID}
            )
        return data


class RoomUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Room."""
    room_type_id = NotFoundPrimaryKeyRelatedField(
        source='room_type',
        queryset=RoomType.objects.all(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Room
        fields = ['room_type_id', 'floor', 'status']

    def validate(self, data):
        if 'status' in data and data['status'] not in dict(Room.STATUS_CHOICES):
            raise serializers.ValidationError(
                {'status': msg.ROOM_STATUS_INVALID}
            )
        return data


class RoomStatusSerializer(serializers.Serializer):
    """Serializer for updating room status."""
    status = serializers.ChoiceField(choices=Room.STATUS_CHOICES)
