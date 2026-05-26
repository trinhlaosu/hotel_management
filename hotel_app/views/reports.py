"""DRF viewsets for this API group."""
from datetime import date

from core import messages as msg
from core.api import api_response
from rest_framework import viewsets
from rest_framework.decorators import action

from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.services.report_service import ReportService


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [SessionAuthenticated, ManagerOnly]

    def _date_range_or_response(self, request):
        tu_ngay = request.GET.get('tu_ngay')
        den_ngay = request.GET.get('den_ngay')
        try:
            tu_ngay_value = date.fromisoformat(tu_ngay) if tu_ngay else None
            den_ngay_value = date.fromisoformat(den_ngay) if den_ngay else None
        except ValueError:
            return None, None, api_response(error=msg.DATE_FORMAT_INVALID, status=400)
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
        try:
            top = int(request.GET.get('top', 5))
        except (TypeError, ValueError):
            return api_response(error='top phai la so nguyen', status=400)
        if top <= 0:
            return api_response(error='top phai lon hon 0', status=400)
        return api_response(data=ReportService().top_dich_vu(top))
