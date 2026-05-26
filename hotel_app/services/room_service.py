"""Room business logic."""
from hotel_app.models import Room, Booking


class RoomService:
    def kiem_tra_trong(self, room_id, check_in, check_out):

        trung_lich = Booking.objects.filter(
            room_id=room_id,
            status__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_o']
        ).filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        return not trung_lich.exists()   # True = còn trống

    def cap_nhat_trang_thai(self, room_id, trang_thai):

        try:
            room = Room.objects.get(id=room_id)
            room.status = trang_thai
            room.save()
            return True, room
        except Room.DoesNotExist:
            return False, None

    def lay_thong_ke_phong(self):

        tat_ca = Room.objects.all()
        return {
            'tong':     tat_ca.count(),
            'trong':    tat_ca.filter(status='trong').count(),
            'co_khach': tat_ca.filter(status='co_khach').count(),
            'bao_tri':  tat_ca.filter(status='bao_tri').count(),
        }

    def loc_queryset(self, queryset, capacity=None, room_type_id=None):
        if capacity:
            queryset = queryset.filter(room_type__capacity__gte=capacity)
        if room_type_id:
            queryset = queryset.filter(room_type_id=room_type_id)
        return queryset

    @property
    def ten_service(self):
        return 'RoomService'

    def __str__(self):
        return f'RoomService()'
