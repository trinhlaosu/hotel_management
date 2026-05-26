"""Employee business logic."""


class EmployeeService:
    def disable(self, employee):
        employee.status = 'nghi_viec'
        employee.save(update_fields=['status', 'updated_at'])

        employee.user.is_active = False
        employee.user.save(update_fields=['is_active', 'updated_at'])

        return employee
