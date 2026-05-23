"""
hotel/services/invoice_service.py
Quản lý nghiệp vụ hóa đơn – Áp dụng ABC + kế thừa + đóng gói
"""
from abc import ABC, abstractmethod


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
    """Quản lý nghiệp vụ hóa đơn – kế thừa ABCInvoiceService"""

    def __tinh_tien(self, booking):
        """(Private) Tính tiền phòng và tiền dịch vụ"""
        from hotel.models import BookingService
        from datetime import date

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
        from hotel.models import Invoice

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
        from hotel.models import Invoice

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
        from hotel.models import Invoice
        from django.utils import timezone

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
