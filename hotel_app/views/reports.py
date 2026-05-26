"""DRF viewsets for this API group."""
from core.api import api_response
from rest_framework import viewsets
from rest_framework.decorators import action

from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.services.report_service import ReportService


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [SessionAuthenticated, ManagerOnly]

    def _date_range_or_response(self, request):
        tu_ngay_value, den_ngay_value, err_msg = ReportService().lay_khoang_ngay(
            request.GET.get('tu_ngay'),
            request.GET.get('den_ngay'),
        )
        if err_msg:
            return None, None, api_response(error=err_msg, status=400)
        return tu_ngay_value, den_ngay_value, None

    @action(detail=False, methods=['get'])
    def revenue(self, request):
        tu_ngay, den_ngay, error = self._date_range_or_response(request)
        if error:
            return error
        return api_response(data=ReportService().thong_ke_doanh_thu(
            tu_ngay, den_ngay))

    @action(detail=False, methods=['get'], url_path='room-status')
    def room_status(self, request):
        return api_response(data=ReportService().thong_ke_trang_thai_phong())

    @action(detail=False, methods=['get'], url_path='booking-statistics')
    def booking_statistics(self, request):
        tu_ngay, den_ngay, error = self._date_range_or_response(request)
        if error:
            return error
        return api_response(data=ReportService().thong_ke_dat_phong(
            tu_ngay, den_ngay))

    @action(detail=False, methods=['get'], url_path='top-services')
    def top_services(self, request):
        top, err_msg = ReportService().lay_top(request.GET.get('top'))
        if err_msg:
            return api_response(error=err_msg, status=400)
        return api_response(data=ReportService().top_dich_vu(top))
