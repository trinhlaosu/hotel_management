"""
test_views.py
=============
Unit test cho 23 API endpoint của hệ thống Quản lý Khách sạn.

Cách chạy:
    python manage.py test hotel.tests.test_views           # toàn bộ
    python manage.py test hotel.tests.test_views.AuthTest  # 1 class
"""

import json
from datetime import date

from django.test import Client, TestCase

from hotel.models import (
    Booking, BookingService, Customer, Department, Employee,
    Invoice, Room, RoomType, Service, User,
)


# =============================================================================
# Helper – dữ liệu mẫu dùng chung cho tất cả test
# =============================================================================

class BaseTest(TestCase):
    """
    Tạo sẵn dữ liệu mẫu trước mỗi test.
    Tất cả test class đều kế thừa class này để không phải lặp code.
    """

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

        # --- Tài khoản ---
        self.quan_ly = User.objects.create(
            username="admin_mychi",
            password="123456",
            email="mychi@hotel.com",
            role="quan_ly",
        )
        self.le_tan = User.objects.create(
            username="nv_chuyen",
            password="123456",
            email="chuyen@hotel.com",
            role="le_tan",
        )

        # --- Phòng ban & nhân viên ---
        self.dept = Department.objects.create(name="Le tan")
        self.emp = Employee.objects.create(
            user=self.le_tan,
            department=self.dept,
            full_name="Vo Mong Chuyen",
            phone="0901111111",
            salary=8_000_000,
            hire_date=date(2024, 1, 1),
        )

        # --- Khách hàng ---
        self.customer = Customer.objects.create(
            full_name="Nguyen Van A",
            phone="0909090901",
            id_card="012345678901",
        )

        # --- Phòng ---
        self.room_type = RoomType.objects.create(
            name="Standard",
            price_per_night=500_000,
            capacity=2,
        )
        self.room = Room.objects.create(
            room_type=self.room_type,
            room_number="101",
            floor=1,
            status="trong",
        )

        # --- Dịch vụ ---
        self.service = Service.objects.create(
            name="An sang",
            price=150_000,
            is_active=True,
        )

    # -------------------------------------------------------------------------
    # Shortcut methods – viết ngắn hơn trong từng test
    # -------------------------------------------------------------------------

    def login(self, username="admin_mychi", password="123456"):
        """Đăng nhập và giữ session cho những request tiếp theo."""
        return self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": username, "password": password}),
            content_type="application/json",
        )

    def post(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

    def put(self, url, data=None):
        return self.client.put(
            url,
            data=json.dumps(data or {}),
            content_type="application/json",
        )

    def _tao_booking(self, check_in="2026-07-01", check_out="2026-07-04"):
        """Tạo booking + trả về booking_id – dùng lại ở nhiều test."""
        res = self.post("/api/bookings/", {
            "customer_id": self.customer.id,
            "room_id":     self.room.id,
            "check_in":    check_in,
            "check_out":   check_out,
        })
        return res.json()["data"]["booking_id"]


# =============================================================================
# API 1 & 2 – Xác thực (đăng nhập / đăng xuất)
# =============================================================================

class AuthTest(BaseTest):
    """
    Test: POST /api/auth/login/
          POST /api/auth/logout/
    """

    # --- API 1: Đăng nhập ---

    def test_01_dang_nhap_thanh_cong(self):
        """Đúng username + password → trả về thông tin user, status 200."""
        res = self.login()

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["username"], "admin_mychi")
        self.assertEqual(data["role"], "quan_ly")

    def test_01_dang_nhap_sai_mat_khau(self):
        """Sai mật khẩu → báo lỗi 400, không vào được hệ thống."""
        res = self.login(password="saimatkhau")

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_01_dang_nhap_thieu_username(self):
        """Bỏ trống username → server từ chối, status 400."""
        res = self.post("/api/auth/login/", {"password": "123456"})

        self.assertEqual(res.status_code, 400)

    def test_01_dang_nhap_user_bi_khoa(self):
        """Tài khoản bị vô hiệu hóa (is_active=False) → không đăng nhập được."""
        self.quan_ly.is_active = False
        self.quan_ly.save()

        res = self.login()
        self.assertEqual(res.status_code, 400)

    # --- API 2: Đăng xuất ---

    def test_02_dang_xuat_thanh_cong(self):
        """Đăng nhập rồi đăng xuất → trả về message thành công."""
        self.login()

        res = self.client.post(
            "/api/auth/logout/",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.json())

    def test_02_sau_dang_xuat_khong_truy_cap_duoc(self):
        """Sau khi đăng xuất, gọi API cần auth → bị từ chối 401."""
        self.login()
        self.client.post("/api/auth/logout/", content_type="application/json")

        res = self.client.get("/api/users/")
        self.assertEqual(res.status_code, 401)


# =============================================================================
# API 3 – Quản lý tài khoản
# =============================================================================

class UserTest(BaseTest):
    """Test: GET /api/users/"""

    def test_03_xem_danh_sach_tai_khoan_quan_ly(self):
        """Quản lý xem được danh sách tài khoản → trả về list, status 200."""
        self.login("admin_mychi")

        res = self.client.get("/api/users/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    def test_03_le_tan_khong_xem_duoc_danh_sach_tai_khoan(self):
        """Le tan khong co quyen xem danh sach tai khoan → bi tu choi 403."""
        self.login("nv_chuyen")

        res = self.client.get("/api/users/")
        self.assertEqual(res.status_code, 403)

    def test_03_chua_dang_nhap_bi_tu_choi(self):
        """Chua dang nhap → 401, khong xem duoc gi."""
        res = self.client.get("/api/users/")
        self.assertEqual(res.status_code, 401)


# =============================================================================
# API 4 & 5 – Quản lý khách hàng
# =============================================================================

class CustomerTest(BaseTest):
    """
    Test: GET  /api/customers/
          POST /api/customers/
    """

    # --- API 4: Xem danh sách ---

    def test_04_xem_danh_sach_khach_hang(self):
        """Nhan vien xem danh sach khach hang → tra ve list, status 200."""
        self.login()

        res = self.client.get("/api/customers/")

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["data"], list)

    def test_04_loc_khach_vip(self):
        """Loc ?customer_type=vip → chi tra ve khach VIP."""
        Customer.objects.create(
            full_name="Khach VIP",
            phone="0888888888",
            id_card="888888888888",
            customer_type="vip",
        )
        self.login()

        res = self.client.get("/api/customers/?customer_type=vip")

        self.assertEqual(res.status_code, 200)
        for kh in res.json()["data"]:
            self.assertEqual(kh["customer_type"], "vip")

    def test_04_tim_kiem_theo_so_dien_thoai(self):
        """Tim ?phone=0909 → tra ve dung khach co so do."""
        self.login()

        res = self.client.get("/api/customers/?phone=0909090901")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertGreaterEqual(len(ds), 1)
        phones = [kh["phone"] for kh in ds]
        self.assertTrue(any("0909090901" in p for p in phones))

    # --- API 5: Thêm khách hàng ---

    def test_05_them_khach_hang_moi(self):
        """Them khach hang voi day du thong tin → 201, luu vao DB."""
        self.login()

        res = self.post("/api/customers/", {
            "full_name": "Tran Thi Moi",
            "phone":     "0777777777",
            "id_card":   "777777777777",
        })

        self.assertEqual(res.status_code, 201)
        self.assertTrue(Customer.objects.filter(phone="0777777777").exists())

    def test_05_them_khach_trung_cccd(self):
        """CCCD da ton tai → bao loi 400, khong tao trung."""
        self.login()

        res = self.post("/api/customers/", {
            "full_name": "Nguoi Khac",
            "phone":     "0666666666",
            "id_card":   "012345678901",
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_05_them_khach_thieu_truong_bat_buoc(self):
        """Thieu id_card → server tu choi, khong tao duoc."""
        self.login()

        res = self.post("/api/customers/", {
            "full_name": "Thieu CCCD",
            "phone":     "0555555555",
        })

        self.assertEqual(res.status_code, 400)


# =============================================================================
# API 6, 7, 8 – Quản lý phòng
# =============================================================================

class RoomTest(BaseTest):
    """
    Test: GET /api/rooms/
          GET /api/rooms/?status=trong
          PUT /api/rooms/<id>/status/
    """

    # --- API 6: Xem danh sách phòng ---

    def test_06_xem_danh_sach_phong(self):
        """Xem tat ca phong → tra ve list co thong tin day du."""
        self.login()

        res = self.client.get("/api/rooms/")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertIsInstance(ds, list)
        self.assertGreaterEqual(len(ds), 1)
        phong = ds[0]
        for field in ["id", "room_number", "status", "room_type", "price_per_night"]:
            self.assertIn(field, phong)

    # --- API 7: Tìm phòng trống ---

    def test_07_loc_phong_con_trong(self):
        """Loc ?status=trong → chi tra ve phong dang trong."""
        Room.objects.create(
            room_type=self.room_type,
            room_number="102",
            floor=1,
            status="co_khach",
        )
        self.login()

        res = self.client.get("/api/rooms/?status=trong")

        self.assertEqual(res.status_code, 200)
        for phong in res.json()["data"]:
            self.assertEqual(phong["status"], "trong")

    def test_07_phong_bao_tri_khong_hien_trong_danh_sach_trong(self):
        """Phong bao tri khong duoc xuat hien khi tim phong trong."""
        Room.objects.create(
            room_type=self.room_type,
            room_number="103",
            floor=1,
            status="bao_tri",
        )
        self.login()

        res = self.client.get("/api/rooms/?status=trong")
        room_numbers = [p["room_number"] for p in res.json()["data"]]

        self.assertNotIn("103", room_numbers)

    # --- API 8: Cập nhật trạng thái phòng ---

    def test_08_cap_nhat_trang_thai_phong(self):
        """Cap nhat phong tu 'trong' → 'bao_tri' → luu dung vao DB."""
        self.login()

        res = self.put(f"/api/rooms/{self.room.id}/status/", {
            "status": "bao_tri",
        })

        self.assertEqual(res.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "bao_tri")

    def test_08_cap_nhat_trang_thai_thieu_status(self):
        """Body khong co truong status → server tu choi 400."""
        self.login()

        res = self.put(f"/api/rooms/{self.room.id}/status/", {})

        self.assertEqual(res.status_code, 400)


# =============================================================================
# API 9 → 14 – Luồng đặt phòng chính
# =============================================================================

class BookingTest(BaseTest):
    """
    Test: GET  /api/bookings/                  (API 9)
          POST /api/bookings/                  (API 10)
          PUT  /api/bookings/<id>/confirm/     (API 11)
          PUT  /api/bookings/<id>/cancel/      (API 12)
          PUT  /api/bookings/<id>/check-in/    (API 13)
          PUT  /api/bookings/<id>/check-out/   (API 14)
    """

    # --- API 9: Xem danh sách đặt phòng ---

    def test_09_xem_danh_sach_dat_phong(self):
        """Nhan vien xem duoc danh sach tat ca booking."""
        self.login()
        self._tao_booking()

        res = self.client.get("/api/bookings/")

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["data"], list)

    def test_09_loc_booking_theo_trang_thai(self):
        """Loc ?status=cho_xac_nhan → chi tra dung trang thai do."""
        self.login()
        self._tao_booking()

        res = self.client.get("/api/bookings/?status=cho_xac_nhan")

        self.assertEqual(res.status_code, 200)
        for b in res.json()["data"]:
            self.assertEqual(b["status"], "cho_xac_nhan")

    # --- API 10: Tạo đặt phòng ---

    def test_10_tao_dat_phong_thanh_cong(self):
        """
        Tao booking day du thong tin, phong con trong
        → 201, tu dong sinh hoa don, tra ve tong tien dung.
        3 dem × 500.000d = 1.500.000d
        """
        self.login()

        res = self.post("/api/bookings/", {
            "customer_id": self.customer.id,
            "room_id":     self.room.id,
            "check_in":    "2026-08-01",
            "check_out":   "2026-08-04",
        })

        self.assertEqual(res.status_code, 201)
        data = res.json()["data"]
        self.assertIn("booking_id", data)
        self.assertEqual(data["tien_phong"], 1_500_000.0)
        self.assertTrue(
            Invoice.objects.filter(booking_id=data["booking_id"]).exists()
        )

    def test_10_tao_dat_phong_check_out_truoc_check_in(self):
        """check_out som hon check_in → du lieu vo ly, phai bao loi 400."""
        self.login()

        res = self.post("/api/bookings/", {
            "customer_id": self.customer.id,
            "room_id":     self.room.id,
            "check_in":    "2026-08-10",
            "check_out":   "2026-08-05",
        })

        self.assertEqual(res.status_code, 400)

    def test_10_tao_dat_phong_phong_da_co_lich(self):
        """
        Phong da duoc dat → khong the tao booking moi trung lich.
        Day la nghiep vu quan trong nhat cua he thong.
        """
        self.login()
        self._tao_booking("2026-09-01", "2026-09-05")

        res = self.post("/api/bookings/", {
            "customer_id": self.customer.id,
            "room_id":     self.room.id,
            "check_in":    "2026-09-03",
            "check_out":   "2026-09-07",
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_10_tao_dat_phong_thieu_customer_id(self):
        """Thieu customer_id → server khong chap nhan, tra loi 400."""
        self.login()

        res = self.post("/api/bookings/", {
            "room_id":   self.room.id,
            "check_in":  "2026-10-01",
            "check_out": "2026-10-03",
        })

        self.assertEqual(res.status_code, 400)

    # --- API 11: Xác nhận đặt phòng ---

    def test_11_xac_nhan_dat_phong(self):
        """Xac nhan booking dang cho → chuyen sang 'da_xac_nhan'."""
        self.login()
        bid = self._tao_booking("2026-10-10", "2026-10-13")

        res = self.put(f"/api/bookings/{bid}/confirm/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "da_xac_nhan")

    def test_11_xac_nhan_booking_dang_o_bi_tu_choi(self):
        """Booking dang co khach khong the xac nhan lan nua → 400."""
        self.login()
        bid = self._tao_booking("2026-10-15", "2026-10-18")
        Booking.objects.filter(id=bid).update(status="dang_o")

        res = self.put(f"/api/bookings/{bid}/confirm/")

        self.assertEqual(res.status_code, 400)

    # --- API 12: Hủy đặt phòng ---

    def test_12_huy_dat_phong(self):
        """Huy booking dang cho xac nhan → trang thai thanh 'da_huy'."""
        self.login()
        bid = self._tao_booking("2026-11-01", "2026-11-03")

        res = self.put(f"/api/bookings/{bid}/cancel/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "da_huy")

    def test_12_huy_booking_dang_o_bi_tu_choi(self):
        """Khach dang o khong the huy giua chung → bao loi."""
        self.login()
        bid = self._tao_booking("2026-11-10", "2026-11-13")
        Booking.objects.filter(id=bid).update(status="dang_o")

        res = self.put(f"/api/bookings/{bid}/cancel/")

        self.assertEqual(res.status_code, 400)

    # --- API 13: Check-in ---

    def test_13_check_in_thanh_cong(self):
        """
        Booking da xac nhan → check-in duoc.
        Ket qua: booking 'dang_o', phong 'co_khach'.
        """
        self.login()
        bid = self._tao_booking("2026-12-01", "2026-12-04")
        self.put(f"/api/bookings/{bid}/confirm/")

        res = self.put(f"/api/bookings/{bid}/check-in/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "dang_o")
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "co_khach")

    def test_13_check_in_chua_xac_nhan_bi_tu_choi(self):
        """Booking chua duoc xac nhan khong the check-in."""
        self.login()
        bid = self._tao_booking("2026-12-10", "2026-12-13")

        res = self.put(f"/api/bookings/{bid}/check-in/")

        self.assertEqual(res.status_code, 400)

    # --- API 14: Check-out ---

    def test_14_check_out_thanh_cong(self):
        """
        Check-out booking dang o → trang thai 'da_tra_phong', phong ve 'trong'.
        Hoa don cung duoc cap nhat lai.
        """
        self.login()
        bid = self._tao_booking("2027-01-01", "2027-01-04")
        self.put(f"/api/bookings/{bid}/confirm/")
        self.put(f"/api/bookings/{bid}/check-in/")

        res = self.put(f"/api/bookings/{bid}/check-out/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "da_tra_phong")
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "trong")

    def test_14_check_out_chua_check_in_bi_tu_choi(self):
        """Khong the check-out neu chua check-in."""
        self.login()
        bid = self._tao_booking("2027-01-10", "2027-01-13")
        self.put(f"/api/bookings/{bid}/confirm/")

        res = self.put(f"/api/bookings/{bid}/check-out/")

        self.assertEqual(res.status_code, 400)


# =============================================================================
# API 15 & 16 – Dịch vụ
# =============================================================================

class ServiceTest(BaseTest):
    """
    Test: GET  /api/services/
          POST /api/bookings/<id>/services/
    """

    # --- API 15: Xem danh sách dịch vụ ---

    def test_15_xem_danh_sach_dich_vu(self):
        """Xem danh sach dich vu dang hoat dong → tra ve list."""
        self.login()

        res = self.client.get("/api/services/")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertIsInstance(ds, list)
        ten = [s["name"] for s in ds]
        self.assertIn("An sang", ten)

    def test_15_dich_vu_bi_xoa_khong_hien(self):
        """Dich vu da xoa mem (is_active=False) khong duoc hien ra."""
        self.service.is_active = False
        self.service.save()
        self.login()

        res = self.client.get("/api/services/")

        ten = [s["name"] for s in res.json()["data"]]
        self.assertNotIn("An sang", ten)

    # --- API 16: Ghi nhận dịch vụ khách sử dụng ---

    def test_16_ghi_nhan_dich_vu_cho_booking(self):
        """
        Khach dung 2 phan an sang (150.000d x 2 = 300.000d)
        → ghi vao DB, cap nhat luon hoa don.
        """
        self.login()
        bid = self._tao_booking("2027-02-01", "2027-02-04")

        res = self.post(f"/api/bookings/{bid}/services/", {
            "service_id": self.service.id,
            "quantity":   2,
        })

        self.assertEqual(res.status_code, 201)
        data = res.json()["data"]
        self.assertEqual(data["subtotal"], 300_000.0)
        self.assertTrue(
            BookingService.objects.filter(booking_id=bid).exists()
        )

    def test_16_ghi_nhan_dich_vu_khong_ton_tai(self):
        """Dich vu ID khong ton tai → bao loi 404."""
        self.login()
        bid = self._tao_booking("2027-02-10", "2027-02-13")

        res = self.post(f"/api/bookings/{bid}/services/", {
            "service_id": 99999,
            "quantity":   1,
        })

        self.assertEqual(res.status_code, 404)


# =============================================================================
# API 17, 18, 19 – Hóa đơn
# =============================================================================

class InvoiceTest(BaseTest):
    """
    Test: POST /api/invoices/
          GET  /api/bookings/<id>/invoice/
          PUT  /api/invoices/<id>/pay/
    """

    def setUp(self):
        super().setUp()
        self.login()
        self.bid = self._tao_booking("2027-03-01", "2027-03-04")
        inv = Invoice.objects.get(booking_id=self.bid)
        self.inv_id = inv.id

    # --- API 17: Lập hóa đơn ---

    def test_17_lap_hoa_don_cho_booking(self):
        """Tao hoa don thu cong cho booking → 201, tra ve thong tin hoa don."""
        bid2 = self._tao_booking("2027-03-10", "2027-03-13")
        Invoice.objects.filter(booking_id=bid2).delete()

        res = self.post("/api/invoices/", {"booking_id": bid2})

        self.assertEqual(res.status_code, 201)
        data = res.json()["data"]
        self.assertIn("total", data)
        self.assertGreater(data["total"], 0)

    def test_17_lap_hoa_don_booking_khong_ton_tai(self):
        """booking_id khong ton tai → 404."""
        res = self.post("/api/invoices/", {"booking_id": 99999})

        self.assertEqual(res.status_code, 404)

    # --- API 18: Xem hóa đơn theo booking ---

    def test_18_xem_hoa_don_theo_booking(self):
        """
        Xem hoa don qua booking_id → tra ve dung thong tin.
        3 dem x 500.000d = 1.500.000d.
        """
        res = self.client.get(f"/api/bookings/{self.bid}/invoice/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(float(data["room_charge"]), 1_500_000.0)
        self.assertEqual(data["payment_status"], "chua_thanh_toan")

    def test_18_booking_chua_co_hoa_don(self):
        """Booking chua co hoa don → tra ve 404."""
        bid2 = self._tao_booking("2027-04-01", "2027-04-04")
        Invoice.objects.filter(booking_id=bid2).delete()

        res = self.client.get(f"/api/bookings/{bid2}/invoice/")

        self.assertEqual(res.status_code, 404)

    # --- API 19: Thanh toán hóa đơn ---

    def test_19_thanh_toan_hoa_don(self):
        """
        Thanh toan bang chuyen khoan → trang thai 'da_thanh_toan',
        luu phuong thuc va thoi gian thanh toan.
        """
        res = self.put(f"/api/invoices/{self.inv_id}/pay/", {
            "payment_method": "chuyen_khoan",
        })

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["payment_method"], "chuyen_khoan")
        self.assertIsNotNone(data["paid_at"])

    def test_19_thanh_toan_lan_2_bi_tu_choi(self):
        """Hoa don da thanh toan, thanh toan lan 2 → bi tu choi 400."""
        self.put(f"/api/invoices/{self.inv_id}/pay/", {
            "payment_method": "tien_mat",
        })
        res = self.put(f"/api/invoices/{self.inv_id}/pay/", {
            "payment_method": "the",
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_19_thanh_toan_hoa_don_khong_ton_tai(self):
        """ID hoa don khong ton tai → 400 (khong crash server)."""
        res = self.put("/api/invoices/99999/pay/", {
            "payment_method": "tien_mat",
        })

        self.assertEqual(res.status_code, 400)


# =============================================================================
# API 20 → 23 – Báo cáo thống kê
# =============================================================================

class ReportTest(BaseTest):
    """
    Test: GET /api/reports/revenue/             (API 20)
          GET /api/reports/room-status/         (API 21)
          GET /api/reports/booking-statistics/  (API 22)
          GET /api/reports/top-services/        (API 23)

    Cac API nay chi danh cho Quan ly.
    """

    # --- API 20: Thống kê doanh thu ---

    def test_20_thong_ke_doanh_thu(self):
        """Quan ly xem thong ke doanh thu → 200, co du truong can thiet."""
        self.login("admin_mychi")

        res = self.client.get("/api/reports/revenue/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("tong_doanh_thu",    data)
        self.assertIn("so_hoa_don_da_tt",  data)

    def test_20_le_tan_khong_xem_duoc_doanh_thu(self):
        """Le tan khong co quyen xem bao cao doanh thu → 403."""
        self.login("nv_chuyen")

        res = self.client.get("/api/reports/revenue/")

        self.assertEqual(res.status_code, 403)

    def test_20_doanh_thu_khi_chua_co_hoa_don(self):
        """Chua co hoa don nao → doanh thu = 0."""
        self.login("admin_mychi")

        res = self.client.get("/api/reports/revenue/")

        data = res.json()["data"]
        self.assertEqual(data["tong_doanh_thu"],   0)
        self.assertEqual(data["so_hoa_don_da_tt"], 0)

    # --- API 21: Thống kê tình trạng phòng ---

    def test_21_thong_ke_trang_thai_phong(self):
        """Thong ke phong → tong = trong + co_khach + bao_tri."""
        self.login("admin_mychi")

        res = self.client.get("/api/reports/room-status/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        for field in ["tong", "trong", "co_khach", "bao_tri"]:
            self.assertIn(field, data)
        self.assertEqual(
            data["tong"],
            data["trong"] + data["co_khach"] + data["bao_tri"],
        )

    # --- API 22: Thống kê đặt phòng ---

    def test_22_thong_ke_dat_phong(self):
        """Thong ke booking → co du cac trang thai."""
        self.login("admin_mychi")
        self._tao_booking("2027-05-01", "2027-05-04")

        res = self.client.get("/api/reports/booking-statistics/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        for field in ["tong", "cho_xac_nhan", "dang_o", "da_tra_phong", "da_huy"]:
            self.assertIn(field, data)
        self.assertGreaterEqual(data["cho_xac_nhan"], 1)

    # --- API 23: Thống kê dịch vụ sử dụng nhiều ---

    def test_23_top_dich_vu(self):
        """Top dich vu → tra ve list, moi phan tu co du thong tin."""
        self.login("admin_mychi")
        bid = self._tao_booking("2027-05-10", "2027-05-13")
        self.post(f"/api/bookings/{bid}/services/", {
            "service_id": self.service.id,
            "quantity":   3,
        })

        res = self.client.get("/api/reports/top-services/")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertIsInstance(ds, list)
        if ds:
            item = ds[0]
            for field in ["ten_dich_vu", "tong_so_luong", "tong_tien"]:
                self.assertIn(field, item)

    def test_23_top_dich_vu_tuy_chinh_so_luong(self):
        """Tham so ?top=3 → tra ve toi da 3 dich vu."""
        self.login("admin_mychi")

        res = self.client.get("/api/reports/top-services/?top=3")

        self.assertEqual(res.status_code, 200)
        self.assertLessEqual(len(res.json()["data"]), 3)
