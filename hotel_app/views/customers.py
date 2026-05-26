"""DRF viewsets for this API group."""
from core import messages as msg
from core.api import ApiResponseModelViewSet

from hotel_app.models import Customer
from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.serializers import (
    CustomerSerializer, CustomerCreateSerializer, CustomerUpdateSerializer
)


class CustomerViewSet(ApiResponseModelViewSet):
    """ViewSet for Customer management."""
    queryset = Customer.objects.filter(is_deleted=False)
    response_serializer_class = CustomerSerializer
    success_messages = {
        'create': msg.CUSTOMER_CREATED,
        'update': msg.CUSTOMER_UPDATED,
        'destroy': msg.CUSTOMER_DELETED,
    }
    filterset_fields = ['customer_type', 'phone', 'id_card']
    search_fields = ['full_name', 'phone', 'id_card', 'email']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'destroy':
            return [SessionAuthenticated(), ManagerOnly()]
        return [SessionAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        return CustomerSerializer
