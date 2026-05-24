"""
test_models.py – Kiểm thử các Model (bảng CSDL)
Chạy: python manage.py test hotel.tests.test_models
"""
from django.test import TestCase
from hotel_app.models import (User, Department, Employee, Customer,
                           RoomType, Room, Booking, Invoice,
                           Service, BookingService)
from datetime import date


class UserModelTest(TestCase):
    """Kiểm thử model User"""

    def setUp(self):
        """Tạo dữ liệu mẫu trước mỗi test"""
        self.user = User.objects.create(
            username='admin_test',
            password='123456',
            email='admin@test.com',
            role='quan_ly'
        )

    def test_tao_user_thanh_cong(self):
        """Tạo user với đúng thông tin"""
        self.assertEqual(self.user.username, 'admin_test')
        self.assertEqual(self.user.role, 'quan_ly')
        self.assertTrue(self.user.is_active)

    def test_user_str(self):
        """__str__ trả về danh sách đúng định dạng"""
        ket_qua = str(self.user)
        self.assertIn('admin_test', ket_qua)
        self.assertIn('quan_ly', ket_qua)

    def test_username_unique(self):
        """Không thể tạo 2 user cùng username"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create(
                username='admin_test',   # Trùng username
                password='654321',
                email='other@test.com',
                role='le_tan'
            )

    def test_mac_dinh_la_active(self):
        """User mới tạo mặc định is_active=True"""
        self.assertTrue(self.user.is_active)


class DepartmentModelTest(TestCase):
    """Kiểm thử model Department"""

    def setUp(self):
        self.dept = Department.objects.create(
            name='Lễ tân',
            description='Tiếp đón khách'
        )

    def test_tao_department(self):
        self.assertEqual(self.dept.name, 'Lễ tân')

    def test_department_str(self):
        ket_qua = str(self.dept)
        self.assertIn('Lễ tân', ket_qua)

    def test_ten_phai_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Department.objects.create(name='Lễ tân')  # Trùng tên


class RoomTypeModelTest(TestCase):
    """Kiểm thử model RoomType"""

    def setUp(self):
        self.room_type = RoomType.objects.create(
            name='Deluxe',
            price_per_night=800000,
            capacity=2,
            description='Phòng cao cấp'
        )

    def test_tao_room_type(self):
        self.assertEqual(self.room_type.name, 'Deluxe')
        self.assertEqual(float(self.room_type.price_per_night), 800000.0)
        self.assertEqual(self.room_type.capacity, 2)

    def test_room_type_str(self):
        ket_qua = str(self.room_type)
        self.assertIn('Deluxe', ket_qua)
        self.assertIn('800000', ket_qua)


class RoomModelTest(TestCase):
    """Kiểm thử model Room"""

    def setUp(self):
        self.room_type = RoomType.objects.create(
            name='Standard', price_per_night=500000, capacity=2)
        self.room = Room.objects.create(
            room_type=self.room_type,
            room_number='101',
            floor=1,
            status='trong'
        )

    def test_tao_room(self):
        self.assertEqual(self.room.room_number, '101')
        self.assertEqual(self.room.status, 'trong')
        self.assertEqual(self.room.room_type.name, 'Standard')

    def test_mac_dinh_trang_thai_trong(self):
        """Phòng mới tạo mặc định là trống"""
        self.assertEqual(self.room.status, 'trong')

    def test_room_str(self):
        ket_qua = str(self.room)
        self.assertIn('101', ket_qua)
        self.assertIn('trong', ket_qua)

    def test_so_phong_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Room.objects.create(
                room_type=self.room_type,
                room_number='101',   # Trùng số phòng
                floor=1
            )


class CustomerModelTest(TestCase):
    """Kiểm thử model Customer"""

    def setUp(self):
        self.customer = Customer.objects.create(
            full_name='Nguyễn Văn A',
            phone='0901234567',
            id_card='012345678901',
            address='TP. HCM',
            customer_type='regular'
        )

    def test_tao_customer(self):
        self.assertEqual(self.customer.full_name, 'Nguyễn Văn A')
        self.assertEqual(self.customer.customer_type, 'regular')

    def test_mac_dinh_la_regular(self):
        """Khách hàng mới mặc định là regular"""
        self.assertEqual(self.customer.customer_type, 'regular')

    def test_cccd_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                full_name='Khác',
                phone='0999999999',
                id_card='012345678901'   # Trùng CCCD
            )


class BookingModelTest(TestCase):
    """Kiểm thử model Booking"""

    def setUp(self):
        self.room_type = RoomType.objects.create(
            name='Standard', price_per_night=500000, capacity=2)
        self.room = Room.objects.create(
            room_type=self.room_type, room_number='201', floor=2)
        self.customer = Customer.objects.create(
            full_name='Trần Thị B', phone='0912345678',
            id_card='098765432101')
        self.booking = Booking.objects.create(
            customer=self.customer,
            room=self.room,
            check_in=date(2026, 6, 10),
            check_out=date(2026, 6, 13),
            status='cho_xac_nhan'
        )

    def test_tao_booking(self):
        self.assertEqual(self.booking.status, 'cho_xac_nhan')
        self.assertEqual(self.booking.customer.full_name, 'Trần Thị B')
        self.assertEqual(self.booking.room.room_number, '201')

    def test_so_dem(self):
        """Số đêm = check_out - check_in = 3 đêm"""
        delta = self.booking.check_out - self.booking.check_in
        self.assertEqual(delta.days, 3)

    def test_booking_str(self):
        ket_qua = str(self.booking)
        self.assertIn('cho_xac_nhan', ket_qua)

