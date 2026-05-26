"""DRF viewsets for service APIs."""
from core import messages as msg
from core.api import ApiResponseModelViewSet, api_response, serializer_error_response
from rest_framework import viewsets

from hotel_app.models import Service
from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.serializers import (
    BookingServiceUpdateSerializer, ServiceCreateSerializer,
    ServiceSerializer, ServiceUpdateSerializer,
)
from hotel_app.services.service_service import HotelServiceService


class ServiceViewSet(ApiResponseModelViewSet):
    queryset = Service.objects.filter(is_deleted=False)
    response_serializer_class = ServiceSerializer
    success_messages = {
        'create': msg.SERVICE_CREATED,
        'update': msg.SERVICE_UPDATED,
        'destroy': msg.SERVICE_DELETED,
    }
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [SessionAuthenticated(), ManagerOnly()]
        return [SessionAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ServiceUpdateSerializer
        return ServiceSerializer

    def perform_destroy(self, service):
        HotelServiceService().deactivate_service(service)


class BookingServiceViewSet(viewsets.GenericViewSet):
    permission_classes = [SessionAuthenticated]

    def update(self, request, pk=None):
        serializer = BookingServiceUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)
        item, err_msg, status_code = HotelServiceService().cap_nhat_booking_service(
            pk, serializer.validated_data)
        if not item:
            return api_response(error=err_msg, status=status_code)
        return api_response(message=msg.SERVICE_UPDATED)

    def destroy(self, request, pk=None):
        item, err_msg = HotelServiceService().xoa_booking_service(pk)
        if not item:
            return api_response(error=err_msg, status=404)
        return api_response(message=msg.SERVICE_DELETED)
