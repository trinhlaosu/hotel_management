"""View API tests."""

from hotel_app.models import Booking, BookingService, Invoice

from ..view_test_base import BaseTest


class BookingTest(BaseTest):


    def test_09_xem_danh_sach_dat_phong(self):
        self.login()
        self._tao_booking()

        res = self.client.get("/api/bookings/")

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["data"], list)

    def test_09_loc_booking_theo_trang_thai(self):
        self.login()
        self._tao_booking()

        res = self.client.get("/api/bookings/?status=cho_xac_nhan")

        self.assertEqual(res.status_code, 200)
        for b in res.json()["data"]:
            self.assertEqual(b["status"], "cho_xac_nhan")

    def test_09_loc_booking_theo_khach_phong_va_khoang_ngay(self):
        self.login()
        self._tao_booking("2026-07-01", "2026-07-04")

        res = self.client.get(
            f"/api/bookings/?customer_id={self.customer.id}"
            f"&room_id={self.room.id}&tu_ngay=2026-07-01&den_ngay=2026-07-04"
        )

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]["room_number"], self.room.room_number)

    def test_09_loc_booking_ngay_khong_hop_le(self):
        self.login()

        res = self.client.get("/api/bookings/?tu_ngay=abc")

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())


    def test_10_tao_dat_phong_thanh_cong(self):
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
        self.login()

        res = self.post("/api/bookings/", {
            "customer_id": self.customer.id,
            "room_id":     self.room.id,
            "check_in":    "2026-08-10",
            "check_out":   "2026-08-05",
        })

        self.assertEqual(res.status_code, 400)

    def test_10_tao_dat_phong_phong_da_co_lich(self):
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
        self.login()

        res = self.post("/api/bookings/", {
            "room_id":   self.room.id,
            "check_in":  "2026-10-01",
            "check_out": "2026-10-03",
        })

        self.assertEqual(res.status_code, 400)


    def test_11_xac_nhan_dat_phong(self):
        self.login()
        bid = self._tao_booking("2026-10-10", "2026-10-13")

        res = self.put(f"/api/bookings/{bid}/confirm/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "da_xac_nhan")

    def test_11_xac_nhan_booking_dang_o_bi_tu_choi(self):
        self.login()
        bid = self._tao_booking("2026-10-15", "2026-10-18")
        Booking.objects.filter(id=bid).update(status="dang_o")

        res = self.put(f"/api/bookings/{bid}/confirm/")

        self.assertEqual(res.status_code, 400)


    def test_12_huy_dat_phong(self):
        self.login()
        bid = self._tao_booking("2026-11-01", "2026-11-03")

        res = self.put(f"/api/bookings/{bid}/cancel/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "da_huy")

    def test_12_huy_booking_dang_o_bi_tu_choi(self):
        self.login()
        bid = self._tao_booking("2026-11-10", "2026-11-13")
        Booking.objects.filter(id=bid).update(status="dang_o")

        res = self.put(f"/api/bookings/{bid}/cancel/")

        self.assertEqual(res.status_code, 400)


    def test_13_check_in_thanh_cong(self):
        self.login()
        bid = self._tao_booking("2026-12-01", "2026-12-04")
        self.put(f"/api/bookings/{bid}/confirm/")

        res = self.put(f"/api/bookings/{bid}/check-in/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "dang_o")
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "co_khach")

    def test_13_check_in_chua_xac_nhan_bi_tu_choi(self):
        self.login()
        bid = self._tao_booking("2026-12-10", "2026-12-13")

        res = self.put(f"/api/bookings/{bid}/check-in/")

        self.assertEqual(res.status_code, 400)


    def test_14_check_out_thanh_cong(self):
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
        self.login()
        bid = self._tao_booking("2027-01-10", "2027-01-13")
        self.put(f"/api/bookings/{bid}/confirm/")

        res = self.put(f"/api/bookings/{bid}/check-out/")

        self.assertEqual(res.status_code, 400)


class ServiceTest(BaseTest):


    def test_15_xem_danh_sach_dich_vu(self):
        self.login()

        res = self.client.get("/api/services/")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertIsInstance(ds, list)
        ten = [s["name"] for s in ds]
        self.assertIn("An sang", ten)

    def test_15_dich_vu_bi_xoa_khong_hien(self):
        self.service.is_active = False
        self.service.save()
        self.login()

        res = self.client.get("/api/services/")

        ten = [s["name"] for s in res.json()["data"]]
        self.assertNotIn("An sang", ten)


    def test_16_ghi_nhan_dich_vu_cho_booking(self):
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
        self.login()
        bid = self._tao_booking("2027-02-10", "2027-02-13")

        res = self.post(f"/api/bookings/{bid}/services/", {
            "service_id": 99999,
            "quantity":   1,
        })

        self.assertEqual(res.status_code, 404)

    def test_16_ghi_nhan_dich_vu_so_luong_khong_hop_le(self):
        self.login()
        bid = self._tao_booking("2027-02-20", "2027-02-23")

        res = self.post(f"/api/bookings/{bid}/services/", {
            "service_id": self.service.id,
            "quantity":   0,
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_16_ghi_nhan_dich_vu_booking_khong_ton_tai(self):
        self.login()

        res = self.post("/api/bookings/99999/services/", {
            "service_id": self.service.id,
            "quantity":   1,
        })

        self.assertEqual(res.status_code, 404)
        self.assertFalse(
            BookingService.objects.filter(booking_id=99999).exists()
        )
