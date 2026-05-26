"""DRF viewsets for this API group."""
from core import messages as msg
from core.api import ApiResponseModelViewSet

from hotel_app.models import Department
from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.serializers import (
    DepartmentSerializer, DepartmentCreateSerializer, DepartmentUpdateSerializer,
)


class DepartmentViewSet(ApiResponseModelViewSet):
    """ViewSet for Department management."""
    queryset = Department.objects.filter(is_deleted=False)
    response_serializer_class = DepartmentSerializer
    success_messages = {
        'create': msg.DEPARTMENT_CREATED,
        'update': msg.DEPARTMENT_UPDATED,
        'destroy': msg.DEPARTMENT_DELETED,
    }
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [SessionAuthenticated(), ManagerOnly()]
        return [SessionAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return DepartmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DepartmentUpdateSerializer
        return DepartmentSerializer
