"""DRF viewsets for this API group."""

from core import messages as msg
from core.api import api_response, serializer_error_response
from rest_framework import viewsets
from rest_framework.decorators import action

from hotel_app.models import Booking
from hotel_app.permissions import SessionAuthenticated
from hotel_app.serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    BookingServiceCreateSerializer,
    BookingServiceSerializer,
    BookingUpdateSerializer,
    InvoiceSerializer,
)
from hotel_app.services.booking_service import (
    BookingService as BookingWorkflowService,
)
from hotel_app.services.invoice_service import InvoiceService
from hotel_app.services.service_service import HotelServiceService


class BookingViewSet(viewsets.GenericViewSet):
    queryset = Booking.objects.select_related(
        'customer',
        'room',
        'room__room_type',
    )
    permission_classes = [SessionAuthenticated]
    filterset_fields = ['status', 'customer', 'room']
    ordering_fields = ['created_at', 'check_in', 'check_out']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        if self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        if self.action == 'services':
            return BookingServiceCreateSerializer
        return BookingSerializer

    def get_booking_service(self):
        return BookingWorkflowService()

    def _booking_data(self, booking, include_financials=False):
        data = BookingSerializer(booking).data
        if include_financials:
            data.update(self.get_booking_service().thong_tin_tai_chinh(booking))
        return data

    def _status_data(self, booking):
        return {
            'id': booking.id,
            'status': booking.status,
        }

    def _created_data(self, booking, invoice):
        return {
            'booking_id': booking.id,
            'status': booking.status,
            'tien_phong': float(invoice.room_charge),
            'tong_tien': float(invoice.total),
        }

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset, err_msg = self.get_booking_service().loc_queryset(
            queryset,
            customer_id=request.query_params.get('customer_id'),
            room_id=request.query_params.get('room_id'),
            tu_ngay=request.query_params.get('tu_ngay'),
            den_ngay=request.query_params.get('den_ngay'),
        )
        if err_msg:
            return api_response(error=err_msg, status=400)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return api_response(
                data=BookingSerializer(page, many=True).data,
                pagination={
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                },
            )
        return api_response(data=BookingSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        booking, err_msg = self.get_booking_service().lay_chi_tiet(pk)
        if not booking:
            return api_response(error=err_msg, status=404)
        return api_response(
            data=self._booking_data(booking, include_financials=True)
        )

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)
        booking, invoice, err_msg = (
            self.get_booking_service().tao_booking_va_hoa_don(
                request.hotel_user,
                serializer.validated_data,
            )
        )
        if not booking:
            return api_response(error=err_msg, status=400)
        return api_response(
            data=self._created_data(booking, invoice),
            message=msg.BOOKING_CREATED,
            status=201,
        )

    def update(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)
        booking, err_msg = self.get_booking_service().cap_nhat_ghi_chu(
            pk,
            serializer.validated_data.get('note', None),
        )
        if not booking:
            return api_response(error=err_msg, status=404)
        return api_response(message=msg.BOOKING_UPDATED)

    def destroy(self, request, pk=None):
        booking, err_msg = self.get_booking_service().huy_booking(pk)
        if not booking:
            return api_response(error=err_msg, status=400)
        return api_response(message=msg.BOOKING_CANCELLED)

    def _workflow(self, pk, service_method, success_message):
        booking, err_msg = service_method(pk)
        if not booking:
            status_code = 404 if err_msg == msg.BOOKING_NOT_FOUND else 400
            return api_response(error=err_msg, status=status_code)
        return api_response(
            data=self._status_data(booking),
            message=success_message,
        )

    @action(detail=True, methods=['put'])
    def confirm(self, request, pk=None):
        return self._workflow(
            pk,
            self.get_booking_service().xac_nhan_booking,
            msg.BOOKING_CONFIRMED,
        )

    @action(detail=True, methods=['put'])
    def cancel(self, request, pk=None):
        return self._workflow(
            pk,
            self.get_booking_service().huy_booking,
            msg.BOOKING_CANCELLED,
        )

    @action(detail=True, methods=['put'], url_path='check-in')
    def check_in(self, request, pk=None):
        return self._workflow(
            pk,
            self.get_booking_service().check_in,
            msg.BOOKING_CHECKED_IN,
        )

    @action(detail=True, methods=['put'], url_path='check-out')
    def check_out(self, request, pk=None):
        return self._workflow(
            pk,
            self.get_booking_service().check_out,
            msg.BOOKING_CHECKED_OUT,
        )

    @action(detail=True, methods=['get', 'post'])
    def services(self, request, pk=None):
        svc = HotelServiceService()
        if request.method == 'GET':
            booking_services = svc.lay_dich_vu_theo_booking(pk)
            return api_response(
                data=BookingServiceSerializer(booking_services, many=True).data
            )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)
        booking_service, err_msg, status_code = svc.them_dich_vu_cho_booking(
            pk, serializer.validated_data)
        if not booking_service:
            return api_response(error=err_msg, status=status_code)
        booking_service = svc.lay_dich_vu_theo_booking(pk).get(
            id=booking_service.id
        )
        return api_response(
            data=BookingServiceSerializer(booking_service).data,
            message=msg.SERVICE_CREATED,
            status=201,
        )

    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        invoice, err_msg = InvoiceService().lay_theo_booking(pk)
        if not invoice:
            return api_response(error=err_msg, status=404)
        data = InvoiceSerializer(invoice).data
        data.pop('payment_method', None)
        data.pop('paid_at', None)
        return api_response(data=data)
