"""
core/utils.py – Tiện ích dùng chung cho toàn hệ thống
"""
import json
from django.http import JsonResponse


def phan_hoi(data=None, message='', status=200, error=''):
    """Chuẩn hóa định dạng JSON trả về"""
    body = {}
    if message:
        body['message'] = message
    if error:
        body['error'] = error
    if data is not None:
        body['data'] = data
    return JsonResponse(body, status=status)


def doc_json(request):
    """Đọc body JSON từ request"""
    try:
        return json.loads(request.body), None
    except Exception:
        return None, phan_hoi(error='JSON không hợp lệ', status=400)


def lay_user_hien_tai(request):
    """Lấy user đang đăng nhập từ session"""
    from hotel.models import User
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None


def kiem_tra_role(request, ds_role):
    """
    Kiểm tra người dùng có role hợp lệ không.
    Trả về (user, None) nếu hợp lệ.
    Trả về (None, JsonResponse lỗi) nếu không hợp lệ.
    """
    user = lay_user_hien_tai(request)
    if not user:
        return None, phan_hoi(error='Chưa đăng nhập', status=401)
    if user.role not in ds_role:
        return None, phan_hoi(error='Không có quyền thực hiện', status=403)
    return user, None


def yeu_cau_dang_nhap(request):
    """Chỉ cần đăng nhập, không kiểm tra role"""
    user = lay_user_hien_tai(request)
    if not user:
        return None, phan_hoi(error='Chưa đăng nhập', status=401)
    return user, None
