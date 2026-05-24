"""Booking workflow APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from hotel_app.services.booking_service import BookingService as BookingWorkflowService
from core.utils import phan_hoi, doc_json, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc, kiem_tra_ngay


@method_decorator(csrf_exempt, name='dispatch')
class BookingView(View):
    def get(self, request, pk=None):
        # GET /api/bookings/ va /api/bookings/<id>/ - xem/loc danh sach booking.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = BookingWorkflowService()
        if pk:
            data, err_msg = svc.lay_chi_tiet(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)

        return phan_hoi(data=svc.lay_danh_sach(
            status=request.GET.get('status'),
            customer_id=request.GET.get('customer_id'),
            room_id=request.GET.get('room_id'),
            tu_ngay=request.GET.get('tu_ngay'),
            den_ngay=request.GET.get('den_ngay'),
        ))

    def post(self, request):
        # POST /api/bookings/ - tao booking va tu dong tao hoa don ban dau.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        ok, msg = kiem_tra_truong_bat_buoc(
            data, ['customer_id', 'room_id', 'check_in', 'check_out'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        ok, msg = kiem_tra_ngay(data['check_in'], data['check_out'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        booking, invoice, err_msg = BookingWorkflowService().tao_booking_va_hoa_don(
            user, data)
        if not booking:
            return phan_hoi(error=err_msg, status=400)

        return phan_hoi(
            data={
                'booking_id': booking.id,
                'status': booking.status,
                'tien_phong': float(invoice.room_charge),
                'tong_tien': float(invoice.total),
            },
            message='Đặt phòng thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/bookings/<id>/ - cap nhat ghi chu booking.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        booking, err_msg = BookingWorkflowService().cap_nhat_ghi_chu(
            pk, data.get('note', None))
        if not booking:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật booking thành công')

    def delete(self, request, pk):
        # DELETE /api/bookings/<id>/ - huy booking neu trang thai cho phep.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        booking, err_msg = BookingWorkflowService().huy_booking(pk)
        if not booking:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(message='Hủy booking thành công')


@method_decorator(csrf_exempt, name='dispatch')
class BookingConfirmView(View):
    """PUT /api/bookings/<pk>/confirm/."""

    def put(self, request, pk):
        # PUT /api/bookings/<id>/confirm/ - xac nhan booking dang cho.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        booking, err_msg = BookingWorkflowService().xac_nhan_booking(pk)
        if not booking:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': booking.id, 'status': booking.status},
            message='Xác nhận đặt phòng thành công',
        )


@method_decorator(csrf_exempt, name='dispatch')
class BookingCancelView(View):
    """PUT /api/bookings/<pk>/cancel/."""

    def put(self, request, pk):
        # PUT /api/bookings/<id>/cancel/ - huy booking qua endpoint rieng.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        booking, err_msg = BookingWorkflowService().huy_booking(pk)
        if not booking:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': booking.id, 'status': booking.status},
            message='Hủy đặt phòng thành công',
        )


@method_decorator(csrf_exempt, name='dispatch')
class BookingCheckinView(View):
    """PUT /api/bookings/<pk>/check-in/."""

    def put(self, request, pk):
        # PUT /api/bookings/<id>/check-in/ - chuyen booking sang dang_o va phong co_khach.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        booking, err_msg = BookingWorkflowService().check_in(pk)
        if not booking:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': booking.id, 'status': booking.status},
            message='Check-in thành công',
        )


@method_decorator(csrf_exempt, name='dispatch')
class BookingCheckoutView(View):
    """PUT /api/bookings/<pk>/check-out/."""

    def put(self, request, pk):
        # PUT /api/bookings/<id>/check-out/ - tra phong va cap nhat hoa don.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        booking, err_msg = BookingWorkflowService().check_out(pk)
        if not booking:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': booking.id, 'status': booking.status},
            message='Check-out thành công',
        )

