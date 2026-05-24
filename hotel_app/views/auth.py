"""Authentication, session, and profile APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.auth_service import AuthService


@method_decorator(csrf_exempt, name='dispatch')
class AuthView(View):
    def post(self, request):
        """POST /api/auth/register/ | login | logout."""
        path = request.path
        svc = AuthService()

        # POST /api/auth/register/ - tao tai khoan le tan, cho quan ly duyet.
        if path.endswith('/register/'):
            data, err = doc_json(request)
            if err:
                return err
            ok, msg = kiem_tra_truong_bat_buoc(
                data, ['username', 'password', 'email'])
            if not ok:
                return phan_hoi(error=msg, status=400)

            user, err_msg = svc.dang_ky(data)
            if not user:
                return phan_hoi(error=err_msg, status=400)
            return phan_hoi(
                data={
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'is_active': user.is_active,
                },
                message='Dang ky thanh cong, vui long cho quan ly duyet',
                status=201,
            )

        # POST /api/auth/login/ - kiem tra username/password va luu session.
        if path.endswith('/login/'):
            data, err = doc_json(request)
            if err:
                return err
            user, err_msg = svc.dang_nhap(
                data.get('username'), data.get('password'))
            if not user:
                return phan_hoi(error=err_msg, status=400)

            request.session['user_id'] = user.id
            request.session['role'] = user.role
            return phan_hoi(
                data={
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role,
                },
                message='Đăng nhập thành công',
            )

        # POST /api/auth/logout/ - xoa session dang nhap hien tai.
        if path.endswith('/logout/'):
            request.session.flush()
            return phan_hoi(message='Đăng xuất thành công')

        return phan_hoi(error='Endpoint không tồn tại', status=404)

    def get(self, request):
        """GET /api/auth/profile/."""
        # GET /api/auth/profile/ - tra ve thong tin user dang dang nhap.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        return phan_hoi(data=AuthService().lay_ho_so(user))

    def put(self, request):
        """PUT /api/auth/profile/ | /api/auth/change-password/."""
        path = request.path
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        svc = AuthService()
        # PUT /api/auth/change-password/ - doi mat khau sau khi xac minh mat khau cu.
        if path.endswith('/change-password/'):
            ok, err_msg = svc.doi_mat_khau(
                user, data.get('old_password'), data.get('new_password'))
            if not ok:
                return phan_hoi(error=err_msg, status=400)
            return phan_hoi(message='Đổi mật khẩu thành công')

        # PUT /api/auth/profile/ - cap nhat email va thong tin nhan vien neu co.
        svc.cap_nhat_ho_so(user, data)
        return phan_hoi(message='Cập nhật hồ sơ thành công')

