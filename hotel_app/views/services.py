"""Hotel service and booking-service APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, kiem_tra_role, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.service_service import HotelServiceService


@method_decorator(csrf_exempt, name='dispatch')
class ServiceView(View):
    def get(self, request, pk=None):
        # GET /api/services/ va /api/services/<id>/ - xem dich vu dang hoat dong/chi tiet.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = HotelServiceService()
        if pk:
            data, err_msg = svc.lay_chi_tiet_dich_vu(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)

        return phan_hoi(data=svc.lay_danh_sach_dich_vu())

    def post(self, request):
        # POST /api/services/ - quan ly them dich vu moi.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name', 'price'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        service = HotelServiceService().tao_dich_vu(data)
        return phan_hoi(
            data={'id': service.id, 'name': service.name},
            message='Thêm dịch vụ thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/services/<id>/ - quan ly cap nhat dich vu.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        service, err_msg = HotelServiceService().cap_nhat_dich_vu(pk, data)
        if not service:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật dịch vụ thành công')

    def delete(self, request, pk):
        # DELETE /api/services/<id>/ - xoa mem dich vu bang is_active=False.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        service, err_msg = HotelServiceService().xoa_mem_dich_vu(pk)
        if not service:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Xóa dịch vụ thành công')


@method_decorator(csrf_exempt, name='dispatch')
class BookingServiceView(View):
    """GET/POST /api/bookings/<pk>/services/."""

    def get(self, request, pk):
        # GET /api/bookings/<id>/services/ - xem cac dich vu da dung cua booking.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        return phan_hoi(
            data=HotelServiceService().lay_dich_vu_theo_booking(pk))

    def post(self, request, pk):
        # POST /api/bookings/<id>/services/ - them dich vu vao booking va cap nhat hoa don.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['service_id', 'quantity'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        booking_service, err_msg, status = (
            HotelServiceService().them_dich_vu_cho_booking(pk, data))
        if not booking_service:
            return phan_hoi(error=err_msg, status=status)
        return phan_hoi(
            data={
                'id': booking_service.id,
                'service': booking_service.service.name,
                'quantity': booking_service.quantity,
                'subtotal': float(booking_service.subtotal),
            },
            message='Thêm dịch vụ thành công',
            status=201,
        )


@method_decorator(csrf_exempt, name='dispatch')
class BookingServiceDetailView(View):
    """PUT/DELETE /api/booking-services/<pk>/."""

    def put(self, request, pk):
        # PUT /api/booking-services/<id>/ - cap nhat so luong dich vu da dung.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        booking_service, err_msg, status = (
            HotelServiceService().cap_nhat_booking_service(pk, data))
        if not booking_service:
            return phan_hoi(error=err_msg, status=status)
        return phan_hoi(message='Cập nhật dịch vụ thành công')

    def delete(self, request, pk):
        # DELETE /api/booking-services/<id>/ - xoa dich vu khoi booking.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        booking_service, err_msg = HotelServiceService().xoa_booking_service(pk)
        if not booking_service:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Xóa dịch vụ thành công')

