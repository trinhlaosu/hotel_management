"""DRF viewsets for this API group."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core import messages as msg
from hotel_app.permissions import SessionAuthenticated
from hotel_app.serializers import (
    ChangePasswordSerializer, LoginSerializer, ProfileUpdateSerializer,
    RegisterSerializer,
)
from hotel_app.services.auth_service import AuthService


class AuthViewSet(viewsets.ViewSet):
    """ViewSet for authentication."""
    
    def get_permissions(self):
        if self.action in ['profile', 'change_password']:
            return [SessionAuthenticated()]
        return []

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user account."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        svc = AuthService()
        user, err_msg = svc.dang_ky(serializer.validated_data)
        if not user:
            return Response(
                {'error': err_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'message': msg.AUTH_REGISTER_SUCCESS,
                'data': svc.user_session_data(user, include_active=True)
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user, err_msg = AuthService().dang_nhap(
            data.get('username'), data.get('password')
        )
        if not user:
            return Response(
                {'error': err_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.session['user_id'] = user.id
        request.session['role'] = user.role
        
        return Response(
            {
                'message': msg.AUTH_LOGIN_SUCCESS,
                'data': AuthService().user_session_data(user)
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user."""
        request.session.flush()
        return Response(
            {'message': msg.AUTH_LOGOUT_SUCCESS},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """Get or update user profile."""
        svc = AuthService()
        
        if request.method == 'GET':
            return Response(
                {'data': svc.lay_ho_so(request.hotel_user)},
                status=status.HTTP_200_OK
            )
        
        serializer = ProfileUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        svc.cap_nhat_ho_so(request.hotel_user, serializer.validated_data)
        
        return Response(
            {'message': msg.AUTH_PROFILE_UPDATE_SUCCESS},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['put'], url_path='change-password')
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ok, err_msg = AuthService().doi_mat_khau(
            request.hotel_user,
            serializer.validated_data.get('old_password'),
            serializer.validated_data.get('new_password'),
        )
        
        if not ok:
            return Response(
                {'error': err_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': msg.AUTH_CHANGE_PASSWORD_SUCCESS},
            status=status.HTTP_200_OK
        )
