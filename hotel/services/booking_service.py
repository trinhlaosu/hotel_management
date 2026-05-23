"""
hotel/services/booking_service.py
Quản lý nghiệp vụ đặt phòng – Áp dụng ABC + kế thừa + đóng gói
"""
from abc import ABC, abstractmethod
from datetime import date


# ── Abstract base ─────────────────────────────────────────────────
class ABCBookingService(ABC):
    """Lớp trừu tượng – interface cho quản lý đặt phòng"""

    @abstractmethod
    def tinh_so_dem(self, check_in, check_out):
        pass

    @abstractmethod
    def tinh_tien_phong(self, booking):
        pass

    @abstractmethod
    def tao_booking(self, data):
        pass


# ── Concrete class ────────────────────────────────────────────────
class BookingService(ABCBookingService):
    """Quản lý nghiệp vụ đặt phòng – kế thừa ABCBookingService"""

    # Đóng gói service phòng bằng thuộc tính protected
    def __init__(self):
        from hotel.services.room_service import RoomService
        self._room_service = RoomService()

    def tinh_so_dem(self, check_in, check_out):
        """Tính số đêm ở"""
        if isinstance(check_in, str):
            check_in = date.fromisoformat(check_in)
        if isinstance(check_out, str):
            check_out = date.fromisoformat(check_out)
        return (check_out - check_in).days

    def tinh_tien_phong(self, booking):
        """Tính tiền phòng = số đêm × giá/đêm"""
        so_dem    = self.tinh_so_dem(booking.check_in, booking.check_out)
        gia_dem   = float(booking.room.room_type.price_per_night)
        return so_dem * gia_dem

    def tinh_tien_dich_vu(self, booking_id):
        """Tính tổng tiền dịch vụ của booking"""
        from hotel.models import BookingService as BS
        ds = BS.objects.filter(booking_id=booking_id)
        return sum(float(dv.subtotal) for dv in ds)

    def tao_booking(self, data):
        """
        Tạo booking mới.
        Kiểm tra phòng trống → tạo booking → trả về (booking, error)
        """
        from hotel.models import Booking, Room
        from datetime import date

        room_id   = data.get('room_id')
        check_in  = date.fromisoformat(data.get('check_in'))
        check_out = date.fromisoformat(data.get('check_out'))

        # Kiểm tra phòng trống
        if not self._room_service.kiem_tra_trong(room_id, check_in, check_out):
            return None, 'Phòng đã có người đặt trong khoảng thời gian này'

        # Tạo booking
        booking = Booking.objects.create(
            customer_id=data.get('customer_id'),
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            status='cho_xac_nhan',
            note=data.get('note', ''),
            created_by_id=data.get('created_by_id'),
        )
        return booking, None

    def xac_nhan_booking(self, booking_id):
        """Xác nhận đặt phòng → chuyển sang 'da_xac_nhan'"""
        from hotel.models import Booking
        try:
            b = Booking.objects.get(id=booking_id)
            if b.status != 'cho_xac_nhan':
                return None, f'Không thể xác nhận khi trạng thái là {b.status}'
            b.status = 'da_xac_nhan'
            b.save()
            return b, None
        except Booking.DoesNotExist:
            return None, 'Không tìm thấy booking'

    def huy_booking(self, booking_id):
        """Hủy đặt phòng"""
        from hotel.models import Booking
        try:
            b = Booking.objects.get(id=booking_id)
            if b.status in ['dang_o', 'da_tra_phong']:
                return None, 'Không thể hủy booking đang/đã ở'
            b.status = 'da_huy'
            b.save()
            # Trả phòng về trống
            self._room_service.cap_nhat_trang_thai(b.room_id, 'trong')
            return b, None
        except Booking.DoesNotExist:
            return None, 'Không tìm thấy booking'

    def check_in(self, booking_id):
        """Check-in → booking → 'dang_o', phòng → 'co_khach'"""
        from hotel.models import Booking
        try:
            b = Booking.objects.get(id=booking_id)
            if b.status != 'da_xac_nhan':
                return None, 'Booking phải được xác nhận trước khi check-in'
            b.status = 'dang_o'
            b.save()
            self._room_service.cap_nhat_trang_thai(b.room_id, 'co_khach')
            return b, None
        except Booking.DoesNotExist:
            return None, 'Không tìm thấy booking'

    def check_out(self, booking_id):
        """Check-out → booking → 'da_tra_phong', phòng → 'trong'"""
        from hotel.models import Booking
        from hotel.services.invoice_service import InvoiceService

        try:
            b = Booking.objects.select_related('room', 'room__room_type').get(
                id=booking_id)
            if b.status != 'dang_o':
                return None, 'Khách chưa check-in'
            b.status = 'da_tra_phong'
            b.save()
            self._room_service.cap_nhat_trang_thai(b.room_id, 'trong')

            # Tự động tạo/cập nhật hóa đơn khi check-out
            inv_svc = InvoiceService()
            inv_svc.cap_nhat_hoa_don(b)

            return b, None
        except Booking.DoesNotExist:
            return None, 'Không tìm thấy booking'

    @property
    def ten_service(self):
        return 'BookingService'

    def __str__(self):
        return 'BookingService()'
