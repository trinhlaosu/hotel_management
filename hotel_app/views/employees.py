"""DRF viewsets for this API group."""
from core import messages as msg
from core.api import ApiResponseModelViewSet

from hotel_app.models import Employee
from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.serializers import (
    EmployeeCreateSerializer, EmployeeSerializer, EmployeeUpdateSerializer,
)
from hotel_app.services.employee_service import EmployeeService


class EmployeeViewSet(ApiResponseModelViewSet):
    """ViewSet for Employee management."""
    queryset = Employee.objects.select_related('user', 'department').filter(
        is_deleted=False
    )
    response_serializer_class = EmployeeSerializer
    success_messages = {
        'create': msg.EMPLOYEE_CREATED,
        'update': msg.EMPLOYEE_UPDATED,
        'destroy': msg.EMPLOYEE_DISABLED,
    }
    filterset_fields = ['department', 'status', 'shift']
    search_fields = ['full_name', 'phone', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'full_name', 'department']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [SessionAuthenticated(), ManagerOnly()]
        return [SessionAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer

    def perform_destroy(self, employee):
        EmployeeService().disable(employee)
