"""Authentication business logic."""
from core import messages as msg
from django.contrib.auth.hashers import check_password, make_password

from hotel_app.models import User, Employee


def ma_hoa_mat_khau(mat_khau):
    return make_password(mat_khau)


def kiem_tra_mat_khau(user, mat_khau):
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
    def lay_ten_hien_thi(self, user):
        try:
            emp = Employee.objects.get(user=user)
            return emp.full_name
        except Employee.DoesNotExist:
            return user.username

    def user_session_data(self, user, include_active=False):
        name = self.lay_ten_hien_thi(user)
        data = {
            'user_id': user.id,
            'username': user.username,
            'full_name': name,
            'role': user.role,
        }
        if include_active:
            data['is_active'] = user.is_active
        return data

    def dang_ky(self, data):
        if User.objects.filter(username=data['username']).exists():
            return None, msg.USERNAME_EXISTS
        if User.objects.filter(email=data['email']).exists():
            return None, msg.EMAIL_EXISTS

        user = User.objects.create(
            username=data['username'],
            password=ma_hoa_mat_khau(data['password']),
            email=data['email'],
            role='le_tan',
            is_active=False,
        )
        return user, None

    def dang_nhap(self, username, password):
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return None, msg.AUTH_INVALID_CREDENTIALS
        if not kiem_tra_mat_khau(user, password):
            return None, msg.AUTH_INVALID_CREDENTIALS
        return user, None

    def lay_ho_so(self, user):
        name = user.username
        try:
            emp = Employee.objects.select_related('department').get(user=user)
            name = emp.full_name
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
        if not kiem_tra_mat_khau(user, mat_khau_cu):
            return False, msg.AUTH_OLD_PASSWORD_WRONG
        user.password = ma_hoa_mat_khau(mat_khau_moi)
        user.save()
        return True, None
