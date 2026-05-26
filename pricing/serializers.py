from rest_framework import serializers

from core.validators import kiem_tra_ngay


class BookingPriceSerializer(serializers.Serializer):
    room_id = serializers.IntegerField(min_value=1)
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    customer_type = serializers.ChoiceField(
        choices=['regular', 'vip'],
        required=False,
        default='regular',
    )

    def validate(self, attrs):
        ok, err_msg = kiem_tra_ngay(
            attrs.get('check_in'),
            attrs.get('check_out'),
        )
        if not ok:
            raise serializers.ValidationError(err_msg)
        return attrs
