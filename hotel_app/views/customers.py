"""Customer management APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, kiem_tra_role, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.customer_service import CustomerService


@method_decorator(csrf_exempt, name='dispatch')
class CustomerView(View):
    def get(self, request, pk=None):
        # GET /api/customers/ va /api/customers/<id>/ - xem/tim/loc khach hang.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = CustomerService()
        if pk:
            data, err_msg = svc.lay_chi_tiet(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)

        return phan_hoi(data=svc.lay_danh_sach(
            customer_type=request.GET.get('customer_type'),
            phone=request.GET.get('phone'),
        ))

    def post(self, request):
        # POST /api/customers/ - them khach hang moi, chan trung phone/CCCD.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        ok, msg = kiem_tra_truong_bat_buoc(
            data, ['full_name', 'phone', 'id_card'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        customer, err_msg = CustomerService().tao_khach_hang(data)
        if not customer:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': customer.id, 'full_name': customer.full_name},
            message='Thêm khách hàng thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/customers/<id>/ - cap nhat thong tin khach hang.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        customer, err_msg = CustomerService().cap_nhat(pk, data)
        if not customer:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật khách hàng thành công')

    def delete(self, request, pk):
        # DELETE /api/customers/<id>/ - quan ly xoa khach hang.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        customer, err_msg = CustomerService().xoa(pk)
        if not customer:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Xóa khách hàng thành công')

