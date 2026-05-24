"""
hotel/services/invoice_service.py
Quản lý nghiệp vụ hóa đơn – Áp dụng ABC + kế thừa + đóng gói
"""
from abc import ABC, abstractmethod
from datetime import date

from django.utils import timezone

from hotel_app.models import Invoice, Booking, BookingService

# ── Abstract base ─────────────────────────────────────────────────
class ABCInvoiceService(ABC):
    """Lớp trừu tượng – interface cho quản lý hóa đơn"""

    @abstractmethod
    def tao_hoa_don(self, booking):
        pass

    @abstractmethod
    def thanh_toan(self, invoice_id, phuong_thuc):
        pass


# ── Concrete class ────────────────────────────────────────────────
class InvoiceService(ABCInvoiceService):
    def to_dict(self, invoice):
        # Chuyen Invoice model thanh dict day du tra ve API.
        return {
            'id': invoice.id,
            'booking_id': invoice.booking_id,
            'customer': invoice.booking.customer.full_name,
            'room_number': invoice.booking.room.room_number,
            'room_charge': float(invoice.room_charge),
            'service_charge': float(invoice.service_charge),
            'total': float(invoice.total),
            'payment_status': invoice.payment_status,
            'payment_method': invoice.payment_method,
            'paid_at': str(invoice.paid_at) if invoice.paid_at else None,
        }

    def to_booking_invoice_dict(self, invoice):
        # Chuyen Invoice thanh dict rut gon khi xem theo booking.
        return {
            'id': invoice.id,
            'booking_id': invoice.booking_id,
            'customer': invoice.booking.customer.full_name,
            'room_number': invoice.booking.room.room_number,
            'room_charge': float(invoice.room_charge),
            'service_charge': float(invoice.service_charge),
            'total': float(invoice.total),
            'payment_status': invoice.payment_status,
        }

    def lay_danh_sach(self):
        # Lay danh sach hoa don.
        qs = Invoice.objects.select_related('booking__customer', 'booking__room')
        return [self.to_dict(invoice) for invoice in qs]

    def lay_chi_tiet(self, invoice_id):
        # Lay chi tiet hoa don theo id.
        try:
            invoice = Invoice.objects.select_related(
                'booking__customer', 'booking__room').get(id=invoice_id)
        except Invoice.DoesNotExist:
            return None, 'Không tìm thấy hóa đơn'
        return self.to_dict(invoice), None

    def tao_hoa_don_thu_cong(self, booking_id):
        # Tao hoa don thu cong tu booking_id.
        try:
            booking = Booking.objects.select_related(
                'room', 'room__room_type').get(id=booking_id)
        except Booking.DoesNotExist:
            return None, 'Không tìm thấy booking'
        invoice = self.tao_hoa_don(booking)
        return self.to_dict(invoice), None

    def lay_theo_booking(self, booking_id):
        # Lay hoa don gan voi mot booking.
        try:
            invoice = Invoice.objects.select_related(
                'booking__customer', 'booking__room').get(booking_id=booking_id)
        except Invoice.DoesNotExist:
            return None, 'Chưa có hóa đơn cho booking này'
        return self.to_booking_invoice_dict(invoice), None

    def __tinh_tien(self, booking):
        """(Private) Tính tiền phòng và tiền dịch vụ"""

        # Tiền phòng = số đêm × giá/đêm
        ci = booking.check_in
        co = booking.check_out
        if isinstance(ci, str):
            ci = date.fromisoformat(ci)
        if isinstance(co, str):
            co = date.fromisoformat(co)

        so_dem     = (co - ci).days
        gia_dem    = float(booking.room.room_type.price_per_night)
        tien_phong = so_dem * gia_dem

        # Tiền dịch vụ
        ds_dv   = BookingService.objects.filter(booking_id=booking.id)
        tien_dv = sum(float(dv.subtotal) for dv in ds_dv)

        return tien_phong, tien_dv

    def tao_hoa_don(self, booking):
        """Tạo hóa đơn mới cho booking"""

        tien_phong, tien_dv = self.__tinh_tien(booking)
        tong = tien_phong + tien_dv

        invoice, _ = Invoice.objects.get_or_create(
            booking=booking,
            defaults={
                'room_charge':    tien_phong,
                'service_charge': tien_dv,
                'total':          tong,
                'payment_status': 'chua_thanh_toan',
            }
        )
        return invoice

    def cap_nhat_hoa_don(self, booking):
        """Tính lại và cập nhật hóa đơn (khi thêm dịch vụ hoặc check-out)"""

        tien_phong, tien_dv = self.__tinh_tien(booking)
        tong = tien_phong + tien_dv

        try:
            inv = Invoice.objects.get(booking=booking)
            inv.room_charge    = tien_phong
            inv.service_charge = tien_dv
            inv.total          = tong
            inv.save()
        except Invoice.DoesNotExist:
            # Nếu chưa có thì tạo mới
            Invoice.objects.create(
                booking=booking,
                room_charge=tien_phong,
                service_charge=tien_dv,
                total=tong,
                payment_status='chua_thanh_toan',
            )

    def thanh_toan(self, invoice_id, phuong_thuc):
        """Cập nhật trạng thái thanh toán"""
        try:
            inv = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return None, 'Không tìm thấy hóa đơn'

        if inv.payment_status == 'da_thanh_toan':
            return None, 'Hóa đơn đã được thanh toán'

        inv.payment_status = 'da_thanh_toan'
        inv.payment_method = phuong_thuc
        inv.paid_at        = timezone.now()
        inv.save()
        return inv, None

    @property
    def ten_service(self):
        return 'InvoiceService'

    def __str__(self):
        return 'InvoiceService()'

