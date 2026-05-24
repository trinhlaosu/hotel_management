"""User account business logic."""
from hotel_app.models import User
from hotel_app.services.auth_service import ma_hoa_mat_khau


class UserService:
    def to_dict(self, user, include_created_at=False):
        # Chuyen User model thanh dict tra ve API.
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
        }
        if include_created_at:
            data['created_at'] = user.created_at
        return data

    def lay_danh_sach(self):
        # Lay toan bo tai khoan cho man hinh quan ly.
        return [self.to_dict(user, include_created_at=True)
                for user in User.objects.all()]

    def lay_chi_tiet(self, user_id):
        # Lay chi tiet mot tai khoan theo id.
        try:
            return self.to_dict(User.objects.get(id=user_id)), None
        except User.DoesNotExist:
            return None, 'Không tìm thấy tài khoản'

    def tao_tai_khoan(self, data):
        # Tao tai khoan noi bo, mat khau duoc hash truoc khi luu.
        if User.objects.filter(username=data['username']).exists():
            return None, 'Username đã tồn tại'
        user = User.objects.create(
            username=data['username'],
            password=ma_hoa_mat_khau(data['password']),
            email=data['email'],
            role=data['role'],
        )
        return user, None

    def cap_nhat(self, user_id, data):
        # Cap nhat thong tin tai khoan va hash password moi neu co.
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None, 'Không tìm thấy tài khoản'

        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        user.is_active = data.get('is_active', user.is_active)
        if data.get('password'):
            user.password = ma_hoa_mat_khau(data['password'])
        user.save()
        return user, None

    def vo_hieu_hoa(self, user_id):
        # Vo hieu hoa tai khoan bang is_active=False.
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None, 'Không tìm thấy tài khoản'
        user.is_active = False
        user.save()
        return user, None

