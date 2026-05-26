"""DRF viewsets for invoice APIs."""
from core import messages as msg
from core.api import ApiResponseModelViewSet, api_response
from rest_framework.decorators import action

from hotel_app.models import Invoice
from hotel_app.permissions import SessionAuthenticated
from hotel_app.serializers import (
    InvoiceCreateSerializer, InvoicePaySerializer, InvoiceSerializer,
)
from hotel_app.services.invoice_service import InvoiceService


class InvoiceViewSet(ApiResponseModelViewSet):
    queryset = Invoice.objects.select_related('booking__customer', 'booking__room')
    permission_classes = [SessionAuthenticated]
    response_serializer_class = InvoiceSerializer
    success_messages = {
        'create': msg.INVOICE_CREATED,
        'update': msg.INVOICE_PAID,
    }
    filterset_fields = ['payment_status', 'payment_method']
    ordering_fields = ['created_at', 'total', 'paid_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        if self.action == 'pay':
            return InvoicePaySerializer
        return InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data['booking']
        invoice = InvoiceService().tao_hoa_don(booking)
        return api_response(
            data=InvoiceSerializer(invoice).data,
            message=msg.INVOICE_CREATED,
            status=201,
        )

    @action(detail=True, methods=['put'])
    def pay(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice, err_msg = InvoiceService().thanh_toan(
            pk,
            serializer.validated_data.get('payment_method', 'tien_mat'),
        )
        if not invoice:
            return api_response(error=err_msg, status=400)
        return api_response(
            data=InvoiceSerializer(invoice).data,
            message=msg.INVOICE_PAID,
        )
