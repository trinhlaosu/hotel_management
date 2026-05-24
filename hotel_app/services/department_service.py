"""Department business logic."""
from hotel_app.models import Department


class DepartmentService:
    def to_dict(self, department):
        # Chuyen Department model thanh dict tra ve API.
        return {
            'id': department.id,
            'name': department.name,
            'description': department.description,
        }

    def lay_danh_sach(self):
        # Lay danh sach phong ban.
        return list(Department.objects.all().values())

    def lay_chi_tiet(self, department_id):
        # Lay chi tiet phong ban theo id.
        try:
            return self.to_dict(Department.objects.get(id=department_id)), None
        except Department.DoesNotExist:
            return None, 'Không tìm thấy phòng ban'

    def tao(self, data):
        # Tao phong ban moi.
        return Department.objects.create(
            name=data['name'],
            description=data.get('description', ''),
        )

    def cap_nhat(self, department_id, data):
        # Cap nhat ten/mo ta phong ban.
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None, 'Không tìm thấy phòng ban'
        department.name = data.get('name', department.name)
        department.description = data.get(
            'description', department.description)
        department.save()
        return department, None

    def xoa(self, department_id):
        # Xoa phong ban theo id.
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None, 'Không tìm thấy phòng ban'
        department.delete()
        return department, None

