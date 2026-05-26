"""Invoice business logic."""
from core import messages as msg
from datetime import date

from django.utils import timezone

from hotel_app.models import Invoice, Booking, BookingService


class InvoiceService:
    def lay_danh_sach(self):
        return Invoice.objects.select_related('booking__customer', 'booking__room')

    def lay_chi_tiet(self, invoice_id):
        try:
            invoice = Invoice.objects.select_related(
                'booking__customer', 'booking__room').get(id=invoice_id)
        except Invoice.DoesNotExist:
            return None, msg.INVOICE_NOT_FOUND
        return invoice, None

    def tao_hoa_don_thu_cong(self, booking_id):
        try:
            booking = Booking.objects.select_related(
                'room', 'room__room_type').get(id=booking_id)
        except Booking.DoesNotExist:
            return None, msg.BOOKING_NOT_FOUND
        invoice = self.tao_hoa_don(booking)
        return invoice, None

    def lay_theo_booking(self, booking_id):
        try:
            invoice = Invoice.objects.select_related(
                'booking__customer', 'booking__room').get(booking_id=booking_id)
        except Invoice.DoesNotExist:
            return None, msg.INVOICE_MISSING_FOR_BOOKING
        return invoice, None

    def __tinh_tien(self, booking):

        ci = booking.check_in
        co = booking.check_out
        if isinstance(ci, str):
            ci = date.fromisoformat(ci)
        if isinstance(co, str):
            co = date.fromisoformat(co)

        so_dem     = (co - ci).days
        gia_dem    = float(booking.room.room_type.price_per_night)
        tien_phong = so_dem * gia_dem

        ds_dv   = BookingService.objects.filter(booking_id=booking.id)
        tien_dv = sum(float(dv.subtotal) for dv in ds_dv)

        return tien_phong, tien_dv

    def tao_hoa_don(self, booking):

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

        tien_phong, tien_dv = self.__tinh_tien(booking)
        tong = tien_phong + tien_dv

        try:
            inv = Invoice.objects.get(booking=booking)
            inv.room_charge    = tien_phong
            inv.service_charge = tien_dv
            inv.total          = tong
            inv.save()
        except Invoice.DoesNotExist:
            Invoice.objects.create(
                booking=booking,
                room_charge=tien_phong,
                service_charge=tien_dv,
                total=tong,
                payment_status='chua_thanh_toan',
            )

    def thanh_toan(self, invoice_id, phuong_thuc):
        try:
            inv = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return None, msg.INVOICE_NOT_FOUND

        if inv.payment_status == 'da_thanh_toan':
            return None, msg.INVOICE_ALREADY_PAID

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
