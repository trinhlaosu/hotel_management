"""View API tests."""

from hotel_app.models import (
    Booking, BookingService, Customer, Department, Employee,
    Invoice, Room, RoomType, Service, User,
)

from ..view_test_base import BaseTest


class FullApiCoverageTest(BaseTest):

    def test_24_auth_register_profile_va_change_password(self):
        res = self.post("/api/auth/register/", {
            "username": "new_reception",
            "password": "abc123",
            "email": "new_reception@hotel.com",
        })
        self.assertEqual(res.status_code, 201)
        self.assertFalse(res.json()["data"]["is_active"])

        self.login("nv_chuyen")
        res = self.client.get("/api/auth/profile/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["username"], "nv_chuyen")

        res = self.put("/api/auth/profile/", {
            "email": "chuyen_new@hotel.com",
            "full_name": "Vo Mong Chuyen Update",
            "phone": "0902222222",
        })
        self.assertEqual(res.status_code, 200)
        self.le_tan.refresh_from_db()
        self.emp.refresh_from_db()
        self.assertEqual(self.le_tan.email, "chuyen_new@hotel.com")
        self.assertEqual(self.emp.phone, "0902222222")

        res = self.put("/api/auth/change-password/", {
            "old_password": "123456",
            "new_password": "654321",
        })
        self.assertEqual(res.status_code, 200)
        self.client.post("/api/auth/logout/", content_type="application/json")
        res = self.login("nv_chuyen", "654321")
        self.assertEqual(res.status_code, 200)

    def test_25_user_crud_detail(self):
        self.login("admin_mychi")
        res = self.post("/api/users/", {
            "username": "user_crud",
            "password": "123456",
            "email": "user_crud@hotel.com",
            "role": "le_tan",
        })
        self.assertEqual(res.status_code, 201)
        user_id = res.json()["data"]["id"]

        res = self.client.get(f"/api/users/{user_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["username"], "user_crud")

        res = self.put(f"/api/users/{user_id}/", {
            "email": "user_crud_new@hotel.com",
            "role": "quan_ly",
            "is_active": True,
        })
        self.assertEqual(res.status_code, 200)
        user = User.objects.get(id=user_id)
        self.assertEqual(user.email, "user_crud_new@hotel.com")
        self.assertEqual(user.role, "quan_ly")

        res = self.delete(f"/api/users/{user_id}/")
        self.assertEqual(res.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_26_department_crud(self):
        self.login("admin_mychi")
        res = self.client.get("/api/departments/")
        self.assertEqual(res.status_code, 200)

        res = self.post("/api/departments/", {
            "name": "Bao ve",
            "description": "An ninh khach san",
        })
        self.assertEqual(res.status_code, 201)
        dept_id = res.json()["data"]["id"]

        res = self.client.get(f"/api/departments/{dept_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["name"], "Bao ve")

        res = self.put(f"/api/departments/{dept_id}/", {
            "name": "Bao ve dem",
            "description": "Ca dem",
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Department.objects.get(id=dept_id).name, "Bao ve dem")

        res = self.delete(f"/api/departments/{dept_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Department.objects.filter(id=dept_id).exists())
        dept = Department.all_objects.get(id=dept_id)
        self.assertTrue(dept.is_deleted)

    def test_27_employee_crud(self):
        self.login("admin_mychi")
        res = self.client.get("/api/employees/")
        self.assertEqual(res.status_code, 200)

        res = self.post("/api/employees/", {
            "username": "emp_crud",
            "password": "123456",
            "email": "emp_crud@hotel.com",
            "department_id": self.dept.id,
            "full_name": "Nhan Vien CRUD",
            "phone": "0903333333",
            "hire_date": "2026-01-01",
            "salary": 9000000,
            "shift": "chieu",
        })
        self.assertEqual(res.status_code, 201)
        emp_id = res.json()["data"]["id"]

        res = self.client.get(f"/api/employees/{emp_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["full_name"], "Nhan Vien CRUD")

        res = self.put(f"/api/employees/{emp_id}/", {
            "full_name": "Nhan Vien Updated",
            "phone": "0904444444",
            "salary": 10000000,
            "shift": "toi",
        })
        self.assertEqual(res.status_code, 200)
        emp = Employee.objects.get(id=emp_id)
        self.assertEqual(emp.full_name, "Nhan Vien Updated")
        self.assertEqual(emp.shift, "toi")

        res = self.delete(f"/api/employees/{emp_id}/")
        self.assertEqual(res.status_code, 200)
        emp.refresh_from_db()
        emp.user.refresh_from_db()
        self.assertEqual(emp.status, "nghi_viec")
        self.assertFalse(emp.user.is_active)

    def test_28_customer_detail_update_delete(self):
        self.login("admin_mychi")
        res = self.client.get(f"/api/customers/{self.customer.id}/")
        self.assertEqual(res.status_code, 200)

        res = self.put(f"/api/customers/{self.customer.id}/", {
            "full_name": "Nguyen Van B",
            "phone": "0909090902",
            "email": "customer@hotel.com",
            "address": "TP HCM",
            "customer_type": "vip",
        })
        self.assertEqual(res.status_code, 200)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.customer_type, "vip")

        res = self.delete(f"/api/customers/{self.customer.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())
        customer = Customer.all_objects.get(id=self.customer.id)
        self.assertTrue(customer.is_deleted)

    def test_29_room_type_crud(self):
        self.login("admin_mychi")
        res = self.client.get("/api/room-types/")
        self.assertEqual(res.status_code, 200)

        res = self.post("/api/room-types/", {
            "name": "Suite CRUD",
            "price_per_night": 1200000,
            "capacity": 3,
            "description": "Phong cao cap",
        })
        self.assertEqual(res.status_code, 201)
        room_type_id = res.json()["data"]["id"]

        res = self.client.get(f"/api/room-types/{room_type_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["name"], "Suite CRUD")

        res = self.put(f"/api/room-types/{room_type_id}/", {
            "name": "Suite Updated",
            "price_per_night": 1300000,
            "capacity": 4,
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(RoomType.objects.get(id=room_type_id).capacity, 4)

        res = self.delete(f"/api/room-types/{room_type_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(RoomType.objects.filter(id=room_type_id).exists())
        room_type = RoomType.all_objects.get(id=room_type_id)
        self.assertTrue(room_type.is_deleted)

    def test_30_room_crud_detail(self):
        self.login("admin_mychi")
        res = self.post("/api/rooms/", {
            "room_type_id": self.room_type.id,
            "room_number": "909",
            "floor": 9,
            "status": "trong",
        })
        self.assertEqual(res.status_code, 201)
        room_id = res.json()["data"]["id"]

        res = self.client.get(f"/api/rooms/{room_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["room_number"], "909")

        res = self.put(f"/api/rooms/{room_id}/", {"floor": 10})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Room.objects.get(id=room_id).floor, 10)

        res = self.delete(f"/api/rooms/{room_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Room.objects.filter(id=room_id).exists())
        room = Room.all_objects.get(id=room_id)
        self.assertTrue(room.is_deleted)

    def test_31_service_crud_detail(self):
        self.login("admin_mychi")
        res = self.post("/api/services/", {
            "name": "Spa CRUD",
            "price": 250000,
            "description": "Dich vu spa",
        })
        self.assertEqual(res.status_code, 201)
        service_id = res.json()["data"]["id"]

        res = self.client.get(f"/api/services/{service_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["name"], "Spa CRUD")

        res = self.put(f"/api/services/{service_id}/", {
            "name": "Spa Updated",
            "price": 300000,
            "description": "Cap nhat",
            "is_active": True,
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Service.objects.get(id=service_id).name, "Spa Updated")

        res = self.delete(f"/api/services/{service_id}/")
        self.assertEqual(res.status_code, 200)
        service = Service.objects.get(id=service_id)
        self.assertFalse(service.is_active)

    def test_32_booking_detail_update_delete(self):
        self.login()
        bid = self._tao_booking("2027-06-01", "2027-06-04")

        res = self.client.get(f"/api/bookings/{bid}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["so_dem"], 3)

        res = self.put(f"/api/bookings/{bid}/", {"note": "Cap nhat ghi chu"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Booking.objects.get(id=bid).note, "Cap nhat ghi chu")

        res = self.delete(f"/api/bookings/{bid}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Booking.objects.get(id=bid).status, "da_huy")

    def test_33_booking_service_get_put_delete(self):
        self.login()
        bid = self._tao_booking("2027-07-01", "2027-07-04")
        add_res = self.post(f"/api/bookings/{bid}/services/", {
            "service_id": self.service.id,
            "quantity": 2,
        })
        self.assertEqual(add_res.status_code, 201)
        bs_id = add_res.json()["data"]["id"]

        res = self.client.get(f"/api/bookings/{bid}/services/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["data"]), 1)

        res = self.put(f"/api/booking-services/{bs_id}/", {"quantity": 3})
        self.assertEqual(res.status_code, 200)
        bs = BookingService.objects.get(id=bs_id)
        self.assertEqual(bs.quantity, 3)
        self.assertEqual(float(bs.subtotal), 450000.0)
        invoice = Invoice.objects.get(booking_id=bid)
        self.assertEqual(float(invoice.service_charge), 450000.0)
        self.assertEqual(float(invoice.total), 1950000.0)

        res = self.delete(f"/api/booking-services/{bs_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(BookingService.objects.filter(id=bs_id).exists())
        invoice.refresh_from_db()
        self.assertEqual(float(invoice.service_charge), 0.0)
        self.assertEqual(float(invoice.total), 1500000.0)

    def test_34_invoice_list_and_detail(self):
        self.login()
        bid = self._tao_booking("2027-08-01", "2027-08-04")
        inv = Invoice.objects.get(booking_id=bid)

        res = self.client.get("/api/invoices/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(any(item["id"] == inv.id for item in res.json()["data"]))

        res = self.client.get(f"/api/invoices/{inv.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["booking_id"], bid)
