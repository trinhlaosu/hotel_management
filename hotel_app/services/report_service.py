"""Report business logic."""
from datetime import date

from core import messages as msg


class ReportService:
    def lay_khoang_ngay(self, tu_ngay=None, den_ngay=None):
        try:
            tu_ngay_value = date.fromisoformat(tu_ngay) if tu_ngay else None
            den_ngay_value = date.fromisoformat(den_ngay) if den_ngay else None
        except ValueError:
            return None, None, msg.DATE_FORMAT_INVALID
        return tu_ngay_value, den_ngay_value, None

    def lay_top(self, top_value=None):
        try:
            top = int(top_value or 5)
        except (TypeError, ValueError):
            return None, 'top phải là số nguyên'
        if top <= 0:
            return None, 'top phải lớn hơn 0'
        return top, None

    def thong_ke_doanh_thu(self, tu_ngay=None, den_ngay=None):
        from hotel_app.models import Invoice
        from django.db.models import Sum

        qs = Invoice.objects.filter(payment_status='da_thanh_toan')
        if tu_ngay:
            qs = qs.filter(paid_at__date__gte=tu_ngay)
        if den_ngay:
            qs = qs.filter(paid_at__date__lte=den_ngay)

        tong = qs.aggregate(tong=Sum('total'))['tong'] or 0
        return {
            'so_hoa_don_da_tt': qs.count(),
            'tong_doanh_thu':   float(tong),
            'tu_ngay':          str(tu_ngay) if tu_ngay else None,
            'den_ngay':         str(den_ngay) if den_ngay else None,
        }

    def thong_ke_trang_thai_phong(self):
        from hotel_app.models import Room
        qs = Room.objects.all()
        return {
            'tong':     qs.count(),
            'trong':    qs.filter(status='trong').count(),
            'co_khach': qs.filter(status='co_khach').count(),
            'bao_tri':  qs.filter(status='bao_tri').count(),
        }

    def thong_ke_dat_phong(self, tu_ngay=None, den_ngay=None):
        from hotel_app.models import Booking

        qs = Booking.objects.all()
        if tu_ngay:
            qs = qs.filter(created_at__date__gte=tu_ngay)
        if den_ngay:
            qs = qs.filter(created_at__date__lte=den_ngay)

        return {
            'tong':          qs.count(),
            'cho_xac_nhan':  qs.filter(status='cho_xac_nhan').count(),
            'da_xac_nhan':   qs.filter(status='da_xac_nhan').count(),
            'dang_o':        qs.filter(status='dang_o').count(),
            'da_tra_phong':  qs.filter(status='da_tra_phong').count(),
            'da_huy':        qs.filter(status='da_huy').count(),
        }

    def top_dich_vu(self, top_n=5):
        from hotel_app.models import BookingService
        from django.db.models import Sum

        qs = (BookingService.objects
              .values('service__id', 'service__name', 'service__price')
              .annotate(tong_sl=Sum('quantity'), tong_tien=Sum('subtotal'))
              .order_by('-tong_sl')[:top_n])

        return list(map(lambda x: {
            'service_id':   x['service__id'],
            'ten_dich_vu':  x['service__name'],
            'gia':          float(x['service__price']),
            'tong_so_luong': x['tong_sl'],
            'tong_tien':    float(x['tong_tien']),
        }, qs))

    @property
    def ten_service(self):
        return 'ReportService'

    def __str__(self):
        return 'ReportService()'
