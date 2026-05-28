"""Booking business logic."""
from core import messages as msg
from datetime import date
from hotel_app.models import Booking, Employee


def _model_id(value):
    return getattr(value, 'id', value)


class BookingService:

    def __init__(self):
        from hotel_app.services.room_service import RoomService
        self._room_service = RoomService()

    def lay_chi_tiet(self, booking_id):
        try:
            booking = Booking.objects.select_related(
                'customer', 'room', 'room__room_type').get(id=booking_id)
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND
        return booking, None

    def thong_tin_tai_chinh(self, booking):
        return {
            'so_dem': self.tinh_so_dem(booking.check_in, booking.check_out),
            'tien_phong': self.tinh_tien_phong(booking),
            'tien_dv': self.tinh_tien_dich_vu(booking.id),
        }

    def lay_danh_sach(self, status=None, customer_id=None, room_id=None,
                      tu_ngay=None, den_ngay=None):
        qs = Booking.objects.select_related(
            'customer', 'room', 'room__room_type').all()
        if status:
            qs = qs.filter(status=status)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if room_id:
            qs = qs.filter(room_id=room_id)
        if tu_ngay:
            qs = qs.filter(check_in__gte=tu_ngay)
        if den_ngay:
            qs = qs.filter(check_out__lte=den_ngay)
        return qs

    def loc_queryset(self, queryset, customer_id=None, room_id=None,
                     tu_ngay=None, den_ngay=None):
        try:
            tu_ngay_value = date.fromisoformat(tu_ngay) if tu_ngay else None
            den_ngay_value = date.fromisoformat(den_ngay) if den_ngay else None
        except ValueError:
            return None, msg.DATE_FORMAT_INVALID

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if tu_ngay_value:
            queryset = queryset.filter(check_in__gte=tu_ngay_value)
        if den_ngay_value:
            queryset = queryset.filter(check_out__lte=den_ngay_value)
        return queryset, None

    def cap_nhat_ghi_chu(self, booking_id, note):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND
        if note is not None:
            booking.note = note
        booking.save()
        return booking, None

    def tinh_so_dem(self, check_in, check_out):
        if isinstance(check_in, str):
            check_in = date.fromisoformat(check_in)
        if isinstance(check_out, str):
            check_out = date.fromisoformat(check_out)
        return (check_out - check_in).days

    def tinh_tien_phong(self, booking):
        from pricing.services import BookingPriceCalculator
        customer_type = booking.customer.customer_type
        result, _ = BookingPriceCalculator().tinh_gia(
            booking.room, booking.check_in, booking.check_out, customer_type
        )
        return result['final_price']

    def tinh_tien_dich_vu(self, booking_id):
        from hotel_app.models import BookingService as BS
        ds = BS.objects.filter(booking_id=booking_id)
        return sum(float(dv.subtotal) for dv in ds)

    def tao_booking(self, data):

        room_id = data.get('room_id') or _model_id(data.get('room'))
        customer_id = data.get('customer_id') or _model_id(data.get('customer'))
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if isinstance(check_in, str):
            check_in = date.fromisoformat(check_in)
        if isinstance(check_out, str):
            check_out = date.fromisoformat(check_out)

        if not self._room_service.kiem_tra_trong(room_id, check_in, check_out):
            return None, msg.BOOKING_ROOM_UNAVAILABLE

        booking = Booking.objects.create(
            customer_id=customer_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            status='cho_xac_nhan',
            note=data.get('note', ''),
            created_by_id=data.get('created_by_id'),
        )
        return booking, None

    def tao_booking_va_hoa_don(self, user, data):
        from hotel_app.services.invoice_service import InvoiceService

        try:
            employee = Employee.objects.get(user=user)
            data['created_by_id'] = employee.id
        except Employee.DoesNotExist:
            data['created_by_id'] = None

        booking, err_msg = self.tao_booking(data)
        if not booking:
            return None, None, err_msg

        booking_full = Booking.objects.select_related(
            'customer', 'room', 'room__room_type').get(id=booking.id)
        invoice = InvoiceService().tao_hoa_don(booking_full)
        return booking, invoice, None

    def xac_nhan_booking(self, booking_id):

        try:
            b = Booking.objects.get(id=booking_id)
            if b.status != 'cho_xac_nhan':
                return None, msg.BOOKING_INVALID_CONFIRM_STATUS.format(status=b.status)
            b.status = 'da_xac_nhan'
            b.save()
            return b, None
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND

    def huy_booking(self, booking_id):

        try:
            b = Booking.objects.get(id=booking_id)
            if b.status in ['dang_o', 'da_tra_phong']:
                return None, msg.BOOKING_INVALID_CANCEL_STATUS
            b.status = 'da_huy'
            b.save()
            self._room_service.cap_nhat_trang_thai(b.room_id, 'trong')
            return b, None
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND

    def check_in(self, booking_id):

        try:
            b = Booking.objects.get(id=booking_id)
            if b.status != 'da_xac_nhan':
                return None, msg.BOOKING_MUST_BE_CONFIRMED
            b.status = 'dang_o'
            b.save()
            self._room_service.cap_nhat_trang_thai(b.room_id, 'co_khach')
            return b, None
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND

    def check_out(self, booking_id):

        from hotel_app.services.invoice_service import InvoiceService

        try:
            b = Booking.objects.select_related(
                'customer', 'room', 'room__room_type').get(id=booking_id)
            if b.status != 'dang_o':
                return None, msg.BOOKING_NOT_CHECKED_IN
            b.status = 'da_tra_phong'
            b.save()
            self._room_service.cap_nhat_trang_thai(b.room_id, 'trong')

            inv_svc = InvoiceService()
            inv_svc.cap_nhat_hoa_don(b)

            return b, None
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND

    @property
    def ten_service(self):
        return 'BookingService'

    def __str__(self):
        return 'BookingService()'
