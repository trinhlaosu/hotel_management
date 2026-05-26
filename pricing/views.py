from core import messages as msg
from core.api import api_response, serializer_error_response
from hotel_app.permissions import SessionAuthenticated
from pricing.serializers import BookingPriceSerializer
from pricing.services import BookingPriceCalculator
from rest_framework import viewsets
from rest_framework.decorators import action


class PricingViewSet(viewsets.ViewSet):
    permission_classes = [SessionAuthenticated]

    @action(detail=False, methods=['post'], url_path='calculate-booking-price')
    def calculate_booking_price(self, request):
        serializer = BookingPriceSerializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)

        calculator = BookingPriceCalculator()
        room = calculator.lay_phong(serializer.validated_data['room_id'])
        if not room:
            return api_response(error=msg.ROOM_NOT_FOUND, status=404)

        data, err_msg = calculator.tinh_gia(
            room,
            serializer.validated_data['check_in'],
            serializer.validated_data['check_out'],
            serializer.validated_data['customer_type'],
        )
        if err_msg:
            return api_response(error=err_msg, status=400)
        return api_response(data=data, message=msg.PRICING_CALCULATED)
