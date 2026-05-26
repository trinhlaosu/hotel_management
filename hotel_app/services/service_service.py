"""Hotel service business logic."""
from core import messages as msg
from hotel_app.models import Booking, Service, BookingService as BookingServiceModel
from hotel_app.services.invoice_service import InvoiceService


def _model_id(value):
    return getattr(value, 'id', value)


class HotelServiceService:
    def deactivate_service(self, service):
        service.is_active = False
        service.save(update_fields=['is_active', 'updated_at'])
        return service

    def lay_dich_vu_theo_booking(self, booking_id):
        return BookingServiceModel.objects.filter(
            booking_id=booking_id).select_related('service')

    def _parse_quantity(self, value):
        try:
            quantity = int(value)
        except (TypeError, ValueError):
            return None, msg.SERVICE_QUANTITY_NOT_INTEGER
        if quantity <= 0:
            return None, msg.SERVICE_QUANTITY_INVALID
        return quantity, None

    def them_dich_vu_cho_booking(self, booking_id, data):
        try:
            booking = Booking.objects.select_related(
                'room', 'room__room_type').get(id=booking_id)
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND, 404

        service_id = data.get('service_id') or _model_id(data.get('service'))
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return None, msg.SERVICE_NOT_FOUND, 404

        quantity, err = self._parse_quantity(data.get('quantity'))
        if err:
            return None, err, 400

        booking_service = BookingServiceModel.objects.create(
            booking_id=booking_id,
            service=service,
            quantity=quantity,
            subtotal=float(service.price) * quantity,
        )

        InvoiceService().cap_nhat_hoa_don(booking)

        return booking_service, None, 201

    def cap_nhat_booking_service(self, booking_service_id, data):
        try:
            booking_service = BookingServiceModel.objects.select_related(
                'service').get(id=booking_service_id)
        except BookingServiceModel.DoesNotExist:
            return None, msg.BOOKING_SERVICE_NOT_FOUND, 404

        quantity, err = self._parse_quantity(
            data.get('quantity', booking_service.quantity))
        if err:
            return None, err, 400

        booking_service.quantity = quantity
        booking_service.subtotal = float(booking_service.service.price) * quantity
        booking_service.save()
        booking = Booking.objects.select_related(
            'room', 'room__room_type').get(id=booking_service.booking_id)
        InvoiceService().cap_nhat_hoa_don(booking)
        return booking_service, None, 200

    def xoa_booking_service(self, booking_service_id):
        try:
            booking_service = BookingServiceModel.objects.get(id=booking_service_id)
        except BookingServiceModel.DoesNotExist:
            return None, msg.BOOKING_SERVICE_NOT_FOUND
        booking = Booking.objects.select_related(
            'room', 'room__room_type').get(id=booking_service.booking_id)
        booking_service.delete()
        InvoiceService().cap_nhat_hoa_don(booking)
        return booking_service, None
