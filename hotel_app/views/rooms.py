"""DRF viewsets for room APIs."""
from core import messages as msg
from core.api import ApiResponseModelViewSet, api_response, serializer_error_response
from rest_framework.decorators import action

from hotel_app.models import Room, RoomType
from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.serializers import (
    RoomCreateSerializer, RoomSerializer, RoomStatusSerializer,
    RoomTypeCreateSerializer, RoomTypeSerializer, RoomTypeUpdateSerializer,
    RoomUpdateSerializer,
)
from hotel_app.services.room_service import RoomService


class RoomTypeViewSet(ApiResponseModelViewSet):
    queryset = RoomType.objects.filter(is_deleted=False)
    response_serializer_class = RoomTypeSerializer
    success_messages = {
        'create': msg.ROOM_TYPE_CREATED,
        'update': msg.ROOM_TYPE_UPDATED,
        'destroy': msg.ROOM_TYPE_DELETED,
    }
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price_per_night', 'capacity', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [SessionAuthenticated(), ManagerOnly()]
        return [SessionAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return RoomTypeCreateSerializer
        if self.action in ['update', 'partial_update']:
            return RoomTypeUpdateSerializer
        return RoomTypeSerializer


class RoomViewSet(ApiResponseModelViewSet):
    queryset = Room.objects.select_related('room_type').filter(is_deleted=False)
    response_serializer_class = RoomSerializer
    success_messages = {
        'create': msg.ROOM_CREATED,
        'update': msg.ROOM_UPDATED,
        'destroy': msg.ROOM_DELETED,
    }
    filterset_fields = ['status', 'room_type', 'floor']
    search_fields = ['room_number']
    ordering_fields = ['floor', 'room_number', 'created_at']
    ordering = ['floor', 'room_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [SessionAuthenticated(), ManagerOnly()]
        return [SessionAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        capacity = self.request.query_params.get('capacity')
        room_type_id = self.request.query_params.get('room_type_id')
        if capacity:
            queryset = queryset.filter(room_type__capacity__gte=capacity)
        if room_type_id:
            queryset = queryset.filter(room_type_id=room_type_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return RoomCreateSerializer
        if self.action in ['update', 'partial_update']:
            return RoomUpdateSerializer
        return RoomSerializer

    @action(detail=True, methods=['put'])
    def status(self, request, pk=None):
        serializer = RoomStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)
        ok, room = RoomService().cap_nhat_trang_thai(
            pk, serializer.validated_data['status'])
        if not ok:
            return api_response(error=msg.ROOM_NOT_FOUND, status=404)
        data = {
            'id': room.id,
            'room_number': room.room_number,
            'status': room.status,
        }
        return api_response(data=data, message=msg.ROOM_STATUS_UPDATED)
