"""Employee business logic."""
from hotel_app.models import User, Employee
from hotel_app.services.auth_service import ma_hoa_mat_khau


class EmployeeService:
    def to_dict(self, employee):
        # Chuyen Employee model thanh dict tra ve API.
        return {
            'id': employee.id,
            'full_name': employee.full_name,
            'phone': employee.phone,
            'department': employee.department.name,
            'shift': employee.shift,
            'salary': float(employee.salary),
            'status': employee.status,
            'username': employee.user.username,
        }

    def lay_danh_sach(self):
        # Lay danh sach nhan vien kem user va phong ban.
        qs = Employee.objects.select_related('user', 'department').all()
        return [self.to_dict(employee) for employee in qs]

    def lay_chi_tiet(self, employee_id):
        # Lay chi tiet nhan vien theo id.
        try:
            employee = Employee.objects.select_related(
                'user', 'department').get(id=employee_id)
        except Employee.DoesNotExist:
            return None, 'Không tìm thấy nhân viên'
        return self.to_dict(employee), None

    def tao(self, data):
        # Tao user le_tan va ho so nhan vien tu cung request.
        user = User.objects.create(
            username=data['username'],
            password=ma_hoa_mat_khau(data['password']),
            email=data['email'],
            role='le_tan',
        )
        employee = Employee.objects.create(
            user=user,
            department_id=data['department_id'],
            full_name=data['full_name'],
            phone=data['phone'],
            salary=data.get('salary', 0),
            hire_date=data['hire_date'],
            shift=data.get('shift', 'sang'),
        )
        return employee

    def cap_nhat(self, employee_id, data):
        # Cap nhat ho so nhan vien.
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return None, 'Không tìm thấy nhân viên'
        employee.full_name = data.get('full_name', employee.full_name)
        employee.phone = data.get('phone', employee.phone)
        employee.salary = data.get('salary', employee.salary)
        employee.shift = data.get('shift', employee.shift)
        employee.status = data.get('status', employee.status)
        if data.get('department_id'):
            employee.department_id = data['department_id']
        employee.save()
        return employee, None

    def vo_hieu_hoa(self, employee_id):
        # Cho nhan vien nghi viec va khoa tai khoan lien ket.
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return None, 'Không tìm thấy nhân viên'
        employee.status = 'nghi_viec'
        employee.save()
        employee.user.is_active = False
        employee.user.save()
        return employee, None

