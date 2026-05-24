"""
hotel/services/room_service.py
Quản lý nghiệp vụ phòng – Áp dụng ABC + kế thừa + đóng gói
"""
from abc import ABC, abstractmethod
from hotel_app.models import Room, RoomType, Booking

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
    def room_type_to_dict(self, room_type, include_description=False):
        # Chuyen RoomType model thanh dict tra ve API.
        data = {
            'id': room_type.id,
            'name': room_type.name,
            'price_per_night': float(room_type.price_per_night),
            'capacity': room_type.capacity,
        }
        if include_description:
            data['description'] = room_type.description
        return data

    def room_to_dict(self, room):
        # Chuyen Room model thanh dict tra ve API.
        return {
            'id': room.id,
            'room_number': room.room_number,
            'floor': room.floor,
            'status': room.status,
            'room_type': room.room_type.name,
            'price_per_night': float(room.room_type.price_per_night),
            'capacity': room.room_type.capacity,
        }

    def lay_danh_sach_loai_phong(self):
        # Lay danh sach loai phong.
        return [self.room_type_to_dict(rt) for rt in RoomType.objects.all()]

    def lay_chi_tiet_loai_phong(self, room_type_id):
        # Lay chi tiet loai phong theo id.
        try:
            return self.room_type_to_dict(
                RoomType.objects.get(id=room_type_id),
                include_description=True,
            ), None
        except RoomType.DoesNotExist:
            return None, 'Không tìm thấy loại phòng'

    def tao_loai_phong(self, data):
        # Tao loai phong moi.
        return RoomType.objects.create(
            name=data['name'],
            price_per_night=data['price_per_night'],
            capacity=data.get('capacity', 2),
            description=data.get('description', ''),
        )

    def cap_nhat_loai_phong(self, room_type_id, data):
        # Cap nhat thong tin loai phong.
        try:
            room_type = RoomType.objects.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return None, 'Không tìm thấy loại phòng'
        room_type.name = data.get('name', room_type.name)
        room_type.price_per_night = data.get(
            'price_per_night', room_type.price_per_night)
        room_type.capacity = data.get('capacity', room_type.capacity)
        room_type.description = data.get('description', room_type.description)
        room_type.save()
        return room_type, None

    def xoa_loai_phong(self, room_type_id):
        # Xoa loai phong theo id.
        try:
            room_type = RoomType.objects.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return None, 'Không tìm thấy loại phòng'
        room_type.delete()
        return room_type, None

    def lay_danh_sach_phong(self, status=None, room_type_id=None, floor=None,
                            capacity=None):
        # Lay danh sach phong, ho tro loc theo trang thai/loai/tang/suc chua.
        qs = Room.objects.select_related('room_type').all()
        if status:
            qs = qs.filter(status=status)
        if room_type_id:
            qs = qs.filter(room_type_id=room_type_id)
        if floor:
            qs = qs.filter(floor=floor)
        if capacity:
            qs = qs.filter(room_type__capacity__gte=capacity)
        return [self.room_to_dict(room) for room in qs]

    def lay_chi_tiet_phong(self, room_id):
        # Lay chi tiet phong theo id.
        try:
            return self.room_to_dict(
                Room.objects.select_related('room_type').get(id=room_id)
            ), None
        except Room.DoesNotExist:
            return None, 'Không tìm thấy phòng'

    def tao_phong(self, data):
        # Tao phong moi, chan trung so phong.
        if Room.objects.filter(room_number=data['room_number']).exists():
            return None, 'Số phòng đã tồn tại'
        room = Room.objects.create(
            room_type_id=data['room_type_id'],
            room_number=data['room_number'],
            floor=data['floor'],
            status=data.get('status', 'trong'),
        )
        return room, None

    def cap_nhat_phong(self, room_id, data):
        # Cap nhat tang hoac loai phong.
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return None, 'Không tìm thấy phòng'
        if data.get('room_type_id'):
            room.room_type_id = data['room_type_id']
        room.floor = data.get('floor', room.floor)
        room.save()
        return room, None

    def xoa_phong(self, room_id):
        # Xoa phong theo id.
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return None, 'Không tìm thấy phòng'
        room.delete()
        return room, None

    def kiem_tra_trong(self, room_id, check_in, check_out):
        """Kiểm tra phòng có trống trong khoảng thời gian không"""

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

        try:
            room = Room.objects.get(id=room_id)
            room.status = trang_thai
            room.save()
            return True, room
        except Room.DoesNotExist:
            return False, None

    def lay_thong_ke_phong(self):
        """Thống kê số lượng phòng theo trạng thái"""

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

