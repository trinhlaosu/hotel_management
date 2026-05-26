"""Booking price calculation module."""
from datetime import timedelta
from decimal import Decimal

from core import messages as msg
from hotel_app.models import Room


class BookingPriceCalculator:
    WEEKEND_RATE = Decimal('0.10')
    VIP_DISCOUNT_RATE = Decimal('0.10')

    def lay_phong(self, room_id):
        try:
            return Room.objects.select_related('room_type').get(
                id=room_id,
                is_deleted=False,
            )
        except Room.DoesNotExist:
            return None

    def tinh_gia(self, room, check_in, check_out, customer_type='regular'):
        so_dem = (check_out - check_in).days
        if so_dem <= 0:
            return None, msg.CHECKOUT_AFTER_CHECKIN

        price_per_night = Decimal(room.room_type.price_per_night)
        weekend_nights = self._count_weekend_nights(check_in, check_out)
        base_price = price_per_night * so_dem
        weekend_fee = price_per_night * self.WEEKEND_RATE * weekend_nights
        subtotal = base_price + weekend_fee
        vip_discount = (
            subtotal * self.VIP_DISCOUNT_RATE
            if customer_type == 'vip' else Decimal('0')
        )
        final_price = subtotal - vip_discount

        return {
            'room_id': room.id,
            'room_number': room.room_number,
            'room_type': room.room_type.name,
            'customer_type': customer_type,
            'check_in': str(check_in),
            'check_out': str(check_out),
            'so_dem': so_dem,
            'weekend_nights': weekend_nights,
            'price_per_night': float(price_per_night),
            'base_price': float(base_price),
            'weekend_fee': float(weekend_fee),
            'vip_discount': float(vip_discount),
            'final_price': float(final_price),
            'formula': (
                'final_price = base_price + weekend_fee - vip_discount'
            ),
        }, None

    def _count_weekend_nights(self, check_in, check_out):
        current = check_in
        count = 0
        while current < check_out:
            if current.weekday() in [5, 6]:
                count += 1
            current += timedelta(days=1)
        return count
