"""Department management APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, kiem_tra_role, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.department_service import DepartmentService


@method_decorator(csrf_exempt, name='dispatch')
class DepartmentView(View):
    def get(self, request, pk=None):
        # GET /api/departments/ va /api/departments/<id>/ - xem phong ban.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = DepartmentService()
        if pk:
            data, err_msg = svc.lay_chi_tiet(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)
        return phan_hoi(data=svc.lay_danh_sach())

    def post(self, request):
        # POST /api/departments/ - quan ly them phong ban moi.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        department = DepartmentService().tao(data)
        return phan_hoi(
            data={'id': department.id, 'name': department.name},
            message='Thêm phòng ban thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/departments/<id>/ - quan ly cap nhat phong ban.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        department, err_msg = DepartmentService().cap_nhat(pk, data)
        if not department:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật phòng ban thành công')

    def delete(self, request, pk):
        # DELETE /api/departments/<id>/ - quan ly xoa phong ban.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        department, err_msg = DepartmentService().xoa(pk)
        if not department:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Xóa phòng ban thành công')

