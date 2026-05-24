"""Authentication and profile business logic."""
from django.contrib.auth.hashers import check_password, make_password

from hotel_app.models import User, Employee


def ma_hoa_mat_khau(mat_khau):
    # Hash mat khau bang Django password hasher truoc khi luu DB.
    return make_password(mat_khau)


def kiem_tra_mat_khau(user, mat_khau):
    # Kiem tra mat khau hash; neu gap password plain cu thi tu dong hash lai.
    if not mat_khau:
        return False
    if check_password(mat_khau, user.password):
        return True
    if user.password == mat_khau:
        user.password = ma_hoa_mat_khau(mat_khau)
        user.save(update_fields=['password'])
        return True
    return False


class AuthService:
    def dang_ky(self, data):
        # Tao tai khoan le_tan moi o trang thai chua active.
        if User.objects.filter(username=data['username']).exists():
            return None, 'Username da ton tai'
        if User.objects.filter(email=data['email']).exists():
            return None, 'Email da ton tai'

        user = User.objects.create(
            username=data['username'],
            password=ma_hoa_mat_khau(data['password']),
            email=data['email'],
            role='le_tan',
            is_active=False,
        )
        return user, None

    def dang_nhap(self, username, password):
        # Tim user active va xac thuc mat khau.
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return None, 'Sai username hoặc mật khẩu'
        if not kiem_tra_mat_khau(user, password):
            return None, 'Sai username hoặc mật khẩu'
        return user, None

    def lay_ho_so(self, user):
        # Tong hop thong tin user va employee neu user co ho so nhan vien.
        try:
            emp = Employee.objects.select_related('department').get(user=user)
            emp_data = {
                'full_name': emp.full_name,
                'phone': emp.phone,
                'department': emp.department.name,
                'shift': emp.shift,
                'salary': float(emp.salary),
            }
        except Employee.DoesNotExist:
            emp_data = None

        return {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'employee': emp_data,
        }

    def cap_nhat_ho_so(self, user, data):
        # Cap nhat email user va thong tin employee neu ton tai.
        user.email = data.get('email', user.email)
        user.save()
        try:
            emp = Employee.objects.get(user=user)
            emp.full_name = data.get('full_name', emp.full_name)
            emp.phone = data.get('phone', emp.phone)
            emp.save()
        except Employee.DoesNotExist:
            pass
        return user

    def doi_mat_khau(self, user, mat_khau_cu, mat_khau_moi):
        # Doi mat khau sau khi xac minh mat khau cu.
        if not kiem_tra_mat_khau(user, mat_khau_cu):
            return False, 'Mật khẩu cũ không đúng'
        user.password = ma_hoa_mat_khau(mat_khau_moi)
        user.save()
        return True, None

