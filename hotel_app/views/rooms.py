"""Room type and room management APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.utils import phan_hoi, doc_json, kiem_tra_role, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc
from hotel_app.services.room_service import RoomService


@method_decorator(csrf_exempt, name='dispatch')
class RoomTypeView(View):
    def get(self, request, pk=None):
        # GET /api/room-types/ va /api/room-types/<id>/ - xem loai phong.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = RoomService()
        if pk:
            data, err_msg = svc.lay_chi_tiet_loai_phong(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)
        return phan_hoi(data=svc.lay_danh_sach_loai_phong())

    def post(self, request):
        # POST /api/room-types/ - quan ly them loai phong moi.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name', 'price_per_night'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        room_type = RoomService().tao_loai_phong(data)
        return phan_hoi(
            data={'id': room_type.id, 'name': room_type.name},
            message='Thêm loại phòng thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/room-types/<id>/ - quan ly cap nhat loai phong.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        room_type, err_msg = RoomService().cap_nhat_loai_phong(pk, data)
        if not room_type:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật loại phòng thành công')

    def delete(self, request, pk):
        # DELETE /api/room-types/<id>/ - quan ly xoa loai phong.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        room_type, err_msg = RoomService().xoa_loai_phong(pk)
        if not room_type:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Xóa loại phòng thành công')


@method_decorator(csrf_exempt, name='dispatch')
class RoomView(View):
    def get(self, request, pk=None):
        # GET /api/rooms/ va /api/rooms/<id>/ - xem/loc phong theo query params.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = RoomService()
        if pk:
            data, err_msg = svc.lay_chi_tiet_phong(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)

        return phan_hoi(data=svc.lay_danh_sach_phong(
            status=request.GET.get('status'),
            room_type_id=request.GET.get('room_type_id'),
            floor=request.GET.get('floor'),
            capacity=request.GET.get('capacity'),
        ))

    def post(self, request):
        # POST /api/rooms/ - quan ly them phong moi, chan trung so phong.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(
            data, ['room_type_id', 'room_number', 'floor'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        room, err_msg = RoomService().tao_phong(data)
        if not room:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(
            data={'id': room.id, 'room_number': room.room_number},
            message='Thêm phòng thành công',
            status=201,
        )

    def put(self, request, pk):
        # PUT /api/rooms/<id>/ - quan ly cap nhat tang/loai phong.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        room, err_msg = RoomService().cap_nhat_phong(pk, data)
        if not room:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Cập nhật phòng thành công')

    def delete(self, request, pk):
        # DELETE /api/rooms/<id>/ - quan ly xoa phong.
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        room, err_msg = RoomService().xoa_phong(pk)
        if not room:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(message='Xóa phòng thành công')


@method_decorator(csrf_exempt, name='dispatch')
class RoomStatusView(View):
    """PUT /api/rooms/<pk>/status/."""

    def put(self, request, pk):
        # PUT /api/rooms/<id>/status/ - cap nhat trang thai phong.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        status = data.get('status')
        if not status:
            return phan_hoi(error='Thiếu trường status', status=400)

        ok, room = RoomService().cap_nhat_trang_thai(pk, status)
        if not ok:
            return phan_hoi(error='Không tìm thấy phòng', status=404)
        return phan_hoi(
            data={'id': room.id, 'room_number': room.room_number,
                  'status': room.status},
            message='Cập nhật trạng thái phòng thành công',
        )

