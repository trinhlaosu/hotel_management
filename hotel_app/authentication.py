"""DRF authentication backed by the app session."""
from rest_framework.authentication import BaseAuthentication

from core.utils import lay_user_hien_tai


class SessionUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = lay_user_hien_tai(request)
        if not user:
            return None
        request.hotel_user = user
        return user, None
