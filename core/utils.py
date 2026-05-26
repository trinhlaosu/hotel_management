"""Ham tien ich dung chung."""
import json
from django.http import JsonResponse

from core import messages as msg


def phan_hoi(data=None, message='', status=200, error=''):
    """Tra ve JSON theo mot mau chung."""
    body = {}
    if message:
        body['message'] = message
    if error:
        body['error'] = error
    if data is not None:
        body['data'] = data
    return JsonResponse(
        body,
        status=status,
        json_dumps_params={'ensure_ascii': False},
    )


def doc_json(request):
    """Doc JSON tu request body."""
    if hasattr(request, 'data'):
        try:
            return request.data, None
        except Exception:
            return None, phan_hoi(error=msg.JSON_INVALID, status=400)
    try:
        return json.loads(request.body), None
    except Exception:
        return None, phan_hoi(error=msg.JSON_INVALID, status=400)


def lay_user_hien_tai(request):
    """Lay user hien tai tu session."""
    from hotel_app.models import User
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None


def kiem_tra_role(request, ds_role):
    """Kiem tra user co dung quyen khong."""
    user = lay_user_hien_tai(request)
    if not user:
        return None, phan_hoi(error=msg.AUTH_REQUIRED, status=401)
    if user.role not in ds_role:
        return None, phan_hoi(error=msg.AUTH_FORBIDDEN, status=403)
    return user, None


def yeu_cau_dang_nhap(request):
    """Kiem tra user da dang nhap."""
    user = lay_user_hien_tai(request)
    if not user:
        return None, phan_hoi(error=msg.AUTH_REQUIRED, status=401)
    return user, None

