"""DRF viewsets for this API group."""
from core import messages as msg
from core.api import ApiResponseModelViewSet, api_response
from rest_framework.decorators import action

from hotel_app.models import User
from hotel_app.permissions import ManagerOnly, SessionAuthenticated
from hotel_app.serializers import (
    UserCreateSerializer, UserSerializer, UserUpdateSerializer,
)
from hotel_app.services.user_service import UserService


class UserViewSet(ApiResponseModelViewSet):
    """ViewSet for User management."""
    queryset = User.objects.select_related().filter(is_deleted=False)
    permission_classes = [SessionAuthenticated, ManagerOnly]
    response_serializer_class = UserSerializer
    success_messages = {
        'create': msg.USER_CREATED,
        'update': msg.USER_UPDATED,
        'destroy': msg.USER_DISABLED,
    }
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def perform_destroy(self, user):
        UserService().disable(user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[SessionAuthenticated, ManagerOnly],
    )
    def disable(self, request, pk=None):
        """Disable a user account."""
        user = UserService().disable(self.get_object())
        return api_response(data=UserSerializer(user).data, message=msg.USER_DISABLED)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[SessionAuthenticated, ManagerOnly],
    )
    def enable(self, request, pk=None):
        """Enable a user account."""
        user = UserService().enable(self.get_object())
        return api_response(data=UserSerializer(user).data, message=msg.USER_UPDATED)
