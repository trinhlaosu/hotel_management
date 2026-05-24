"""Report APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from hotel_app.services.report_service import ReportService
from core.utils import phan_hoi, kiem_tra_role


@method_decorator(csrf_exempt, name='dispatch')
class ReportView(View):
    """
    GET /api/reports/revenue/
    GET /api/reports/room-status/
    GET /api/reports/booking-statistics/
    GET /api/reports/top-services/
    """

    def get(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        path = request.path
        svc = ReportService()

        # GET /api/reports/revenue/ - thong ke doanh thu.
        if path.endswith('/revenue/'):
            tu_ngay = request.GET.get('tu_ngay')
            den_ngay = request.GET.get('den_ngay')
            return phan_hoi(data=svc.thong_ke_doanh_thu(tu_ngay, den_ngay))

        # GET /api/reports/room-status/ - thong ke so phong theo trang thai.
        if path.endswith('/room-status/'):
            return phan_hoi(data=svc.thong_ke_trang_thai_phong())

        # GET /api/reports/booking-statistics/ - thong ke booking theo trang thai.
        if path.endswith('/booking-statistics/'):
            tu_ngay = request.GET.get('tu_ngay')
            den_ngay = request.GET.get('den_ngay')
            return phan_hoi(data=svc.thong_ke_dat_phong(tu_ngay, den_ngay))

        # GET /api/reports/top-services/ - thong ke dich vu duoc dung nhieu.
        if path.endswith('/top-services/'):
            top_n = int(request.GET.get('top', 5))
            return phan_hoi(data=svc.top_dich_vu(top_n))

        return phan_hoi(error='Endpoint khong ton tai', status=404)

