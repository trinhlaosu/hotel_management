"""Hotel service and booking-service business logic."""
from hotel_app.models import Booking, Service, BookingService as BookingServiceModel
from hotel_app.services.invoice_service import InvoiceService


class HotelServiceService:
    def service_to_dict(self, service, include_active=False):
        # Chuyen Service model thanh dict tra ve API.
        data = {
            'id': service.id,
            'name': service.name,
            'price': float(service.price),
            'description': service.description,
        }
        if include_active:
            data['is_active'] = service.is_active
        return data

    def lay_danh_sach_dich_vu(self):
        # Lay danh sach dich vu dang hoat dong.
        return [self.service_to_dict(service)
                for service in Service.objects.filter(is_active=True)]

    def lay_chi_tiet_dich_vu(self, service_id):
        # Lay chi tiet mot dich vu theo id.
        try:
            return self.service_to_dict(
                Service.objects.get(id=service_id),
                include_active=True,
            ), None
        except Service.DoesNotExist:
            return None, 'Không tìm thấy dịch vụ'

    def tao_dich_vu(self, data):
        # Tao dich vu moi.
        service = Service.objects.create(
            name=data['name'],
            price=data['price'],
            description=data.get('description', ''),
        )
        return service

    def cap_nhat_dich_vu(self, service_id, data):
        # Cap nhat thong tin dich vu.
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return None, 'Không tìm thấy dịch vụ'
        service.name = data.get('name', service.name)
        service.price = data.get('price', service.price)
        service.description = data.get('description', service.description)
        service.is_active = data.get('is_active', service.is_active)
        service.save()
        return service, None

    def xoa_mem_dich_vu(self, service_id):
        # Xoa mem dich vu bang is_active=False.
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return None, 'Không tìm thấy dịch vụ'
        service.is_active = False
        service.save()
        return service, None

    def booking_service_to_dict(self, booking_service):
        # Chuyen BookingService model thanh dict tra ve API.
        return {
            'id': booking_service.id,
            'service': booking_service.service.name,
            'quantity': booking_service.quantity,
            'subtotal': float(booking_service.subtotal),
            'used_at': str(booking_service.used_at),
        }

    def lay_dich_vu_theo_booking(self, booking_id):
        # Lay cac dich vu da ghi nhan cho mot booking.
        qs = BookingServiceModel.objects.filter(
            booking_id=booking_id).select_related('service')
        return [self.booking_service_to_dict(item) for item in qs]

    def _parse_quantity(self, value):
        # Parse va validate so luong dich vu phai la so nguyen duong.
        try:
            quantity = int(value)
        except (TypeError, ValueError):
            return None, 'Số lượng dịch vụ phải là số nguyên'
        if quantity <= 0:
            return None, 'Số lượng dịch vụ phải lớn hơn 0'
        return quantity, None

    def them_dich_vu_cho_booking(self, booking_id, data):
        # Them dich vu vao booking va cap nhat lai hoa don neu co booking.
        try:
            service = Service.objects.get(id=data['service_id'])
        except Service.DoesNotExist:
            return None, 'Không tìm thấy dịch vụ', 404

        quantity, err = self._parse_quantity(data.get('quantity'))
        if err:
            return None, err, 400

        booking_service = BookingServiceModel.objects.create(
            booking_id=booking_id,
            service=service,
            quantity=quantity,
            subtotal=float(service.price) * quantity,
        )

        try:
            booking = Booking.objects.select_related(
                'room', 'room__room_type').get(id=booking_id)
            InvoiceService().cap_nhat_hoa_don(booking)
        except Booking.DoesNotExist:
            pass

        return booking_service, None, 201

    def cap_nhat_booking_service(self, booking_service_id, data):
        # Cap nhat so luong dich vu da dung va tinh lai subtotal.
        try:
            booking_service = BookingServiceModel.objects.select_related(
                'service').get(id=booking_service_id)
        except BookingServiceModel.DoesNotExist:
            return None, 'Không tìm thấy', 404

        quantity, err = self._parse_quantity(
            data.get('quantity', booking_service.quantity))
        if err:
            return None, err, 400

        booking_service.quantity = quantity
        booking_service.subtotal = float(booking_service.service.price) * quantity
        booking_service.save()
        return booking_service, None, 200

    def xoa_booking_service(self, booking_service_id):
        # Xoa mot dong dich vu da ghi nhan khoi booking.
        try:
            booking_service = BookingServiceModel.objects.get(id=booking_service_id)
        except BookingServiceModel.DoesNotExist:
            return None, 'Không tìm thấy'
        booking_service.delete()
        return booking_service, None

