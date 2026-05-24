"""Employee management APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, kiem_tra_role, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.employee_service import EmployeeService


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeView(View):
    def get(self, request, pk=None):
        # GET /api/employees/ va /api/employees/<id>/ - xem nhan vien.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = EmployeeService()
        if pk:
            data, err_msg = svc.lay_chi_tiet(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)
        return phan_hoi(data=svc.lay_danh_sach())

    def post(self, request):
        # POST /api/employees/ - quan ly tao user le tan va ho so nhan vien.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(
            data,
            ['username', 'password', 'email', 'department_id',
             'full_name', 'phone', 'hire_date'],
        )
        if not ok:
            return phan_hoi(error=msg, status=400)

        employee = EmployeeService().tao(data)
        return phan_hoi(
            data={'id': employee.id, 'full_name': employee.full_name},
            message='Thêm nhân viên thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/employees/<id>/ - quan ly cap nhat ho so nhan vien.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        employee, err_msg = EmployeeService().cap_nhat(pk, data)
        if not employee:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật nhân viên thành công')

    def delete(self, request, pk):
        # DELETE /api/employees/<id>/ - cho nhan vien nghi viec va khoa user.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        employee, err_msg = EmployeeService().vo_hieu_hoa(pk)
        if not employee:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Đã vô hiệu hóa nhân viên')

