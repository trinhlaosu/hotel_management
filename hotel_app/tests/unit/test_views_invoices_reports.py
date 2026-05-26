"""View API tests."""

from hotel_app.models import Invoice

from ..view_test_base import BaseTest


class InvoiceTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.login()
        self.bid = self._tao_booking("2027-03-01", "2027-03-04")
        inv = Invoice.objects.get(booking_id=self.bid)
        self.inv_id = inv.id


    def test_17_lap_hoa_don_cho_booking(self):
        bid2 = self._tao_booking("2027-03-10", "2027-03-13")
        Invoice.objects.filter(booking_id=bid2).delete()

        res = self.post("/api/invoices/", {"booking_id": bid2})

        self.assertEqual(res.status_code, 201)
        data = res.json()["data"]
        self.assertIn("total", data)
        self.assertGreater(data["total"], 0)

    def test_17_lap_hoa_don_booking_khong_ton_tai(self):
        res = self.post("/api/invoices/", {"booking_id": 99999})

        self.assertEqual(res.status_code, 404)


    def test_18_xem_hoa_don_theo_booking(self):
        res = self.client.get(f"/api/bookings/{self.bid}/invoice/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(float(data["room_charge"]), 1_500_000.0)
        self.assertEqual(data["payment_status"], "chua_thanh_toan")

    def test_18_booking_chua_co_hoa_don(self):
        bid2 = self._tao_booking("2027-04-01", "2027-04-04")
        Invoice.objects.filter(booking_id=bid2).delete()

        res = self.client.get(f"/api/bookings/{bid2}/invoice/")

        self.assertEqual(res.status_code, 404)


    def test_19_thanh_toan_hoa_don(self):
        res = self.put(f"/api/invoices/{self.inv_id}/pay/", {
            "payment_method": "chuyen_khoan",
        })

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["payment_method"], "chuyen_khoan")
        self.assertIsNotNone(data["paid_at"])

    def test_19_thanh_toan_lan_2_bi_tu_choi(self):
        self.put(f"/api/invoices/{self.inv_id}/pay/", {
            "payment_method": "tien_mat",
        })
        res = self.put(f"/api/invoices/{self.inv_id}/pay/", {
            "payment_method": "the",
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_19_thanh_toan_hoa_don_khong_ton_tai(self):
        res = self.put("/api/invoices/99999/pay/", {
            "payment_method": "tien_mat",
        })

        self.assertEqual(res.status_code, 400)


class ReportTest(BaseTest):


    def test_20_thong_ke_doanh_thu(self):
        self.login("admin_mychi")

        res = self.client.get("/api/reports/revenue/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("tong_doanh_thu",    data)
        self.assertIn("so_hoa_don_da_tt",  data)

    def test_20_le_tan_khong_xem_duoc_doanh_thu(self):
        self.login("nv_chuyen")

        res = self.client.get("/api/reports/revenue/")

        self.assertEqual(res.status_code, 403)

    def test_20_doanh_thu_khi_chua_co_hoa_don(self):
        self.login("admin_mychi")

        res = self.client.get("/api/reports/revenue/")

        data = res.json()["data"]
        self.assertEqual(data["tong_doanh_thu"],   0)
        self.assertEqual(data["so_hoa_don_da_tt"], 0)

    def test_20_doanh_thu_ngay_khong_hop_le(self):
        self.login("admin_mychi")

        res = self.client.get("/api/reports/revenue/?tu_ngay=abc")

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())


    def test_21_thong_ke_trang_thai_phong(self):
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


    def test_22_thong_ke_dat_phong(self):
        self.login("admin_mychi")
        self._tao_booking("2027-05-01", "2027-05-04")

        res = self.client.get("/api/reports/booking-statistics/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        for field in ["tong", "cho_xac_nhan", "dang_o", "da_tra_phong", "da_huy"]:
            self.assertIn(field, data)
        self.assertGreaterEqual(data["cho_xac_nhan"], 1)

    def test_22_thong_ke_dat_phong_ngay_khong_hop_le(self):
        self.login("admin_mychi")

        res = self.client.get("/api/reports/booking-statistics/?den_ngay=abc")

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())


    def test_23_top_dich_vu(self):
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
        self.login("admin_mychi")

        res = self.client.get("/api/reports/top-services/?top=3")

        self.assertEqual(res.status_code, 200)
        self.assertLessEqual(len(res.json()["data"]), 3)

    def test_23_top_dich_vu_so_luong_khong_hop_le(self):
        self.login("admin_mychi")

        res = self.client.get("/api/reports/top-services/?top=abc")

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())
