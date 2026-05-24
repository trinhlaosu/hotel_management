"""User account management APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, kiem_tra_role
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.user_service import UserService


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    def get(self, request, pk=None):
        # GET /api/users/ va /api/users/<id>/ - quan ly xem danh sach/chi tiet user.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        svc = UserService()
        if pk:
            data, err_msg = svc.lay_chi_tiet(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)

        return phan_hoi(data=svc.lay_danh_sach())

    def post(self, request):
        # POST /api/users/ - quan ly tao tai khoan noi bo moi.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        ok, msg = kiem_tra_truong_bat_buoc(
            data, ['username', 'password', 'email', 'role'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        new_user, err_msg = UserService().tao_tai_khoan(data)
        if not new_user:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': new_user.id, 'username': new_user.username},
            message='Tạo tài khoản thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/users/<id>/ - cap nhat email, role, active, password neu co.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        updated_user, err_msg = UserService().cap_nhat(pk, data)
        if not updated_user:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật tài khoản thành công')

    def delete(self, request, pk):
        # DELETE /api/users/<id>/ - vo hieu hoa tai khoan thay vi xoa cung.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        disabled_user, err_msg = UserService().vo_hieu_hoa(pk)
        if not disabled_user:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Vô hiệu hóa tài khoản thành công')

