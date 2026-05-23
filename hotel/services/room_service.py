"""
hotel/services/room_service.py
Quản lý nghiệp vụ phòng – Áp dụng ABC + kế thừa + đóng gói
"""
from abc import ABC, abstractmethod


# ── Abstract base ─────────────────────────────────────────────────
class ABCRoomService(ABC):
    """Lớp trừu tượng – interface cho quản lý phòng"""

    @abstractmethod
    def kiem_tra_trong(self, room_id, check_in, check_out):
        pass

    @abstractmethod
    def cap_nhat_trang_thai(self, room_id, trang_thai):
        pass


# ── Concrete class ────────────────────────────────────────────────
class RoomService(ABCRoomService):
    """Quản lý nghiệp vụ phòng – kế thừa ABCRoomService"""

    def kiem_tra_trong(self, room_id, check_in, check_out):
        """Kiểm tra phòng có trống trong khoảng thời gian không"""
        from hotel.models import Booking

        # Tìm các booking trùng lịch
        trung_lich = Booking.objects.filter(
            room_id=room_id,
            status__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_o']
        ).filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        return not trung_lich.exists()   # True = còn trống

    def cap_nhat_trang_thai(self, room_id, trang_thai):
        """Cập nhật trạng thái phòng vào CSDL"""
        from hotel.models import Room

        try:
            room = Room.objects.get(id=room_id)
            room.status = trang_thai
            room.save()
            return True, room
        except Room.DoesNotExist:
            return False, None

    def lay_thong_ke_phong(self):
        """Thống kê số lượng phòng theo trạng thái"""
        from hotel.models import Room

        tat_ca = Room.objects.all()
        return {
            'tong':     tat_ca.count(),
            'trong':    tat_ca.filter(status='trong').count(),
            'co_khach': tat_ca.filter(status='co_khach').count(),
            'bao_tri':  tat_ca.filter(status='bao_tri').count(),
        }

    @property
    def ten_service(self):
        return 'RoomService'

    def __str__(self):
        return f'RoomService()'
