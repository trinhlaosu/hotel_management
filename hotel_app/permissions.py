"""DRF permissions based on the app session user."""
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import BasePermission

from core import messages as msg


class SessionNotAuthenticated(APIException):
    status_code = 401
    default_detail = msg.AUTH_REQUIRED
    default_code = 'not_authenticated'


class SessionAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'hotel_user', None)
        if not user:
            raise SessionNotAuthenticated()
        return True


class ManagerOnly(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'hotel_user', None)
        if not user:
            raise SessionNotAuthenticated()
        if user.role != 'quan_ly':
            raise PermissionDenied(msg.AUTH_FORBIDDEN)
        return True
