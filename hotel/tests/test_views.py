"""
test_views.py – Kiểm thử Views (API endpoints)
Chạy: python manage.py test hotel.tests.test_views
"""
import json
from django.test import TestCase, Client
from hotel.models import (User, Department, Employee, Customer,
                           RoomType, Room, Booking, Invoice, Service)
from datetime import date


class BaseViewTest(TestCase):
    """Dữ liệu mẫu + helper dùng chung cho tất cả view test"""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

        # Tạo user Quản lý
        self.quan_ly = User.objects.create(
            username='quan_ly', password='123456',
            email='ql@test.com', role='quan_ly')

        # Tạo user Lễ tân
        self.le_tan = User.objects.create(
            username='le_tan', password='123456',
            email='lt@test.com', role='le_tan')

        # Dữ liệu hỗ trợ
        self.dept = Department.objects.create(name='Lễ tân test')

        self.room_type = RoomType.objects.create(
            name='Standard test', price_per_night=500000, capacity=2)

        self.room = Room.objects.create(
            room_type=self.room_type,
            room_number='T01', floor=1, status='trong')

        self.customer = Customer.objects.create(
            full_name='Khách Test', phone='0909090901',
            id_card='999999999901')

        self.service = Service.objects.create(
            name='Ăn sáng test', price=150000, is_active=True)

    def dang_nhap(self, username='quan_ly', password='123456'):
        """Helper: đăng nhập và giữ session"""
        res = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json'
        )
        return res

    def post_json(self, url, data):
        return self.client.post(url,
            data=json.dumps(data), content_type='application/json')

    def put_json(self, url, data=None):
        return self.client.put(url,
            data=json.dumps(data or {}), content_type='application/json')


# ──────────────────────────────────────────────────────────────────
#  Auth Views
# ──────────────────────────────────────────────────────────────────
class AuthViewTest(BaseViewTest):

    def test_dang_nhap_thanh_cong(self):
        """Đăng nhập đúng thông tin → 200"""
        res = self.dang_nhap('quan_ly', '123456')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('data', data)
        self.assertEqual(data['data']['username'], 'quan_ly')
        self.assertEqual(data['data']['role'], 'quan_ly')

    def test_dang_nhap_sai_mat_khau(self):
        """Đăng nhập sai mật khẩu → 400"""
        res = self.post_json('/api/auth/login/',
                             {'username': 'quan_ly', 'password': 'sai'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', res.json())

    def test_dang_nhap_user_khong_ton_tai(self):
        """Đăng nhập user không tồn tại → 400"""
        res = self.post_json('/api/auth/login/',
                             {'username': 'khong_co', 'password': '123456'})
        self.assertEqual(res.status_code, 400)

    def test_dang_xuat(self):
        """Đăng xuất → 200"""
        self.dang_nhap()
        res = self.client.post('/api/auth/logout/',
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_xem_profile_chua_dang_nhap(self):
        """Xem profile khi chưa đăng nhập → 401"""
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, 401)

    def test_xem_profile_sau_dang_nhap(self):
        """Xem profile sau đăng nhập → 200 có data"""
        self.dang_nhap()
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertEqual(data['username'], 'quan_ly')


# ──────────────────────────────────────────────────────────────────
#  Room Views
# ──────────────────────────────────────────────────────────────────
class RoomViewTest(BaseViewTest):

    def test_xem_danh_sach_phong_chua_dang_nhap(self):
        """Xem phòng khi chưa đăng nhập → 401"""
        res = self.client.get('/api/rooms/')
        self.assertEqual(res.status_code, 401)

    def test_xem_danh_sach_phong(self):
        """Xem danh sách phòng → 200, có data"""
        self.dang_nhap()
        res = self.client.get('/api/rooms/')
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_loc_phong_trong(self):
        """Lọc phòng theo status=trong"""
        self.dang_nhap()
        res = self.client.get('/api/rooms/?status=trong')
        self.assertEqual(res.status_code, 200)
        ds = res.json()['data']
        for phong in ds:
            self.assertEqual(phong['status'], 'trong')

    def test_them_phong_voi_quyen_quan_ly(self):
        """Thêm phòng với quyền Quản lý → 201"""
        self.dang_nhap('quan_ly')
        res = self.post_json('/api/rooms/', {
            'room_type_id': self.room_type.id,
            'room_number': 'T99',
            'floor': 9
        })
        self.assertEqual(res.status_code, 201)
        self.assertIn('T99', str(res.json()))

    def test_them_phong_voi_quyen_le_tan(self):
        """Lễ tân không có quyền thêm phòng → 403"""
        self.dang_nhap('le_tan')
        res = self.post_json('/api/rooms/', {
            'room_type_id': self.room_type.id,
            'room_number': 'T98',
            'floor': 9
        })
        self.assertEqual(res.status_code, 403)

    def test_them_phong_trung_so_phong(self):
        """Thêm phòng trùng số phòng → 400"""
        self.dang_nhap('quan_ly')
        res = self.post_json('/api/rooms/', {
            'room_type_id': self.room_type.id,
            'room_number': 'T01',   # Đã tồn tại
            'floor': 1
        })
        self.assertEqual(res.status_code, 400)

    def test_cap_nhat_trang_thai_phong(self):
        """Cập nhật trạng thái phòng → 200"""
        self.dang_nhap()
        res = self.put_json(f'/api/rooms/{self.room.id}/status/',
                            {'status': 'bao_tri'})
        self.assertEqual(res.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'bao_tri')


# ──────────────────────────────────────────────────────────────────
#  Customer Views
# ──────────────────────────────────────────────────────────────────
class CustomerViewTest(BaseViewTest):

    def test_them_khach_hang(self):
        """Thêm khách hàng mới → 201"""
        self.dang_nhap()
        res = self.post_json('/api/customers/', {
            'full_name': 'Nguyễn Thị Mới',
            'phone':     '0888888888',
            'id_card':   '888888888888'
        })
        self.assertEqual(res.status_code, 201)

    def test_them_khach_hang_trung_cccd(self):
        """CCCD đã tồn tại → 400"""
        self.dang_nhap()
        res = self.post_json('/api/customers/', {
            'full_name': 'Người Khác',
            'phone':     '0777777777',
            'id_card':   '999999999901'   # Trùng CCCD
        })
        self.assertEqual(res.status_code, 400)

    def test_loc_khach_vip(self):
        """Lọc khách VIP theo query param"""
        Customer.objects.create(
            full_name='Khách VIP', phone='0666666666',
            id_card='666666666666', customer_type='vip')
        self.dang_nhap()
        res = self.client.get('/api/customers/?customer_type=vip')
        self.assertEqual(res.status_code, 200)
        ds = res.json()['data']
        for kh in ds:
            self.assertEqual(kh['customer_type'], 'vip')

    def test_tim_theo_so_dien_thoai(self):
        """Tìm khách theo số điện thoại"""
        self.dang_nhap()
        res = self.client.get('/api/customers/?phone=0909090901')
        self.assertEqual(res.status_code, 200)
        ds = res.json()['data']
        self.assertGreaterEqual(len(ds), 1)


# ──────────────────────────────────────────────────────────────────
#  Booking Views
# ──────────────────────────────────────────────────────────────────
class BookingViewTest(BaseViewTest):

    def test_tao_dat_phong(self):
        """Tạo đặt phòng thành công → 201 + tự tạo hóa đơn"""
        self.dang_nhap()
        res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-07-10',
            'check_out':   '2026-07-13'
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()['data']
        self.assertIn('booking_id', data)
        self.assertIn('tien_phong', data)
        self.assertEqual(data['tien_phong'], 1500000.0)  # 3 × 500.000

    def test_tao_dat_phong_thieu_truong(self):
        """Thiếu trường bắt buộc → 400"""
        self.dang_nhap()
        res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            # Thiếu room_id, check_in, check_out
        })
        self.assertEqual(res.status_code, 400)

    def test_tao_dat_phong_ngay_sai(self):
        """check_out trước check_in → 400"""
        self.dang_nhap()
        res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-07-13',
            'check_out':   '2026-07-10'   # Sai thứ tự
        })
        self.assertEqual(res.status_code, 400)

    def test_xac_nhan_booking(self):
        """Xác nhận đặt phòng → status = da_xac_nhan"""
        self.dang_nhap()
        # Tạo booking trước
        create_res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-08-01',
            'check_out':   '2026-08-04'
        })
        booking_id = create_res.json()['data']['booking_id']

        # Xác nhận
        res = self.put_json(f'/api/bookings/{booking_id}/confirm/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['data']['status'], 'da_xac_nhan')

    def test_check_in(self):
        """Check-in → status = dang_o"""
        self.dang_nhap()
        create_res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-09-01',
            'check_out':   '2026-09-04'
        })
        booking_id = create_res.json()['data']['booking_id']

        # Xác nhận trước
        self.put_json(f'/api/bookings/{booking_id}/confirm/')
        # Check-in
        res = self.put_json(f'/api/bookings/{booking_id}/check-in/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['data']['status'], 'dang_o')

    def test_huy_booking(self):
        """Hủy booking → status = da_huy"""
        self.dang_nhap()
        create_res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-10-01',
            'check_out':   '2026-10-03'
        })
        booking_id = create_res.json()['data']['booking_id']

        res = self.client.delete(f'/api/bookings/{booking_id}/')
        self.assertEqual(res.status_code, 200)
        b = Booking.objects.get(id=booking_id)
        self.assertEqual(b.status, 'da_huy')

    def test_them_dich_vu_cho_booking(self):
        """Thêm dịch vụ cho booking → 201"""
        self.dang_nhap()
        create_res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-11-01',
            'check_out':   '2026-11-03'
        })
        booking_id = create_res.json()['data']['booking_id']

        res = self.post_json(f'/api/bookings/{booking_id}/services/', {
            'service_id': self.service.id,
            'quantity':   2
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['data']['subtotal'], 300000.0)


# ──────────────────────────────────────────────────────────────────
#  Invoice Views
# ──────────────────────────────────────────────────────────────────
class InvoiceViewTest(BaseViewTest):

    def setUp(self):
        super().setUp()
        self.dang_nhap()
        # Tạo booking + hóa đơn mẫu
        create_res = self.post_json('/api/bookings/', {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-06-10',
            'check_out':   '2026-06-13'
        })
        self.booking_id = create_res.json()['data']['booking_id']
        # Lấy invoice id
        inv = Invoice.objects.get(booking_id=self.booking_id)
        self.invoice_id = inv.id

    def test_xem_hoa_don_theo_booking(self):
        """Xem hóa đơn theo booking_id → 200"""
        res = self.client.get(f'/api/bookings/{self.booking_id}/invoice/')
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertEqual(float(data['room_charge']), 1500000.0)
        self.assertEqual(data['payment_status'], 'chua_thanh_toan')

    def test_thanh_toan(self):
        """Thanh toán hóa đơn → payment_status = da_thanh_toan"""
        res = self.put_json(f'/api/invoices/{self.invoice_id}/pay/',
                            {'payment_method': 'chuyen_khoan'})
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertEqual(data['payment_method'], 'chuyen_khoan')
        self.assertIsNotNone(data['paid_at'])

    def test_thanh_toan_2_lan(self):
        """Thanh toán lần 2 → 400"""
        self.put_json(f'/api/invoices/{self.invoice_id}/pay/',
                      {'payment_method': 'tien_mat'})
        res = self.put_json(f'/api/invoices/{self.invoice_id}/pay/',
                            {'payment_method': 'the'})
        self.assertEqual(res.status_code, 400)


# ──────────────────────────────────────────────────────────────────
#  Report Views
# ──────────────────────────────────────────────────────────────────
class ReportViewTest(BaseViewTest):

    def test_thong_ke_trang_thai_phong_quan_ly(self):
        """Quản lý xem thống kê phòng → 200"""
        self.dang_nhap('quan_ly')
        res = self.client.get('/api/reports/room-status/')
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertIn('tong', data)

    def test_thong_ke_le_tan_bi_tu_choi(self):
        """Lễ tân không được xem reports → 403"""
        self.dang_nhap('le_tan')
        res = self.client.get('/api/reports/revenue/')
        self.assertEqual(res.status_code, 403)

    def test_thong_ke_doanh_thu(self):
        """Thống kê doanh thu → 200 có đúng key"""
        self.dang_nhap('quan_ly')
        res = self.client.get('/api/reports/revenue/')
        self.assertEqual(res.status_code, 200)
        data = res.json()['data']
        self.assertIn('tong_doanh_thu', data)
        self.assertIn('so_hoa_don_da_tt', data)

    def test_thong_ke_dat_phong(self):
        """Thống kê booking → 200"""
        self.dang_nhap('quan_ly')
        res = self.client.get('/api/reports/booking-statistics/')
        self.assertEqual(res.status_code, 200)

    def test_top_dich_vu(self):
        """Top dịch vụ → 200"""
        self.dang_nhap('quan_ly')
        res = self.client.get('/api/reports/top-services/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()['data'], list)
