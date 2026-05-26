"""View API tests."""

from ..view_test_base import BaseTest


class AuthTest(BaseTest):


    def test_01_dang_nhap_thanh_cong(self):
        res = self.login()

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["username"], "admin_mychi")
        self.assertEqual(data["role"], "quan_ly")

    def test_01_dang_nhap_sai_mat_khau(self):
        res = self.login(password="saimatkhau")

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_01_dang_nhap_thieu_username(self):
        res = self.post("/api/auth/login/", {"password": "123456"})

        self.assertEqual(res.status_code, 400)

    def test_01_dang_nhap_user_bi_khoa(self):
        self.quan_ly.is_active = False
        self.quan_ly.save()

        res = self.login()
        self.assertEqual(res.status_code, 400)


    def test_02_dang_xuat_thanh_cong(self):
        self.login()

        res = self.client.post(
            "/api/auth/logout/",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.json())

    def test_02_sau_dang_xuat_khong_truy_cap_duoc(self):
        self.login()
        self.client.post("/api/auth/logout/", content_type="application/json")

        res = self.client.get("/api/users/")
        self.assertEqual(res.status_code, 401)


class UserTest(BaseTest):

    def test_03_xem_danh_sach_tai_khoan_quan_ly(self):
        self.login("admin_mychi")

        res = self.client.get("/api/users/")

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    def test_03_le_tan_khong_xem_duoc_danh_sach_tai_khoan(self):
        self.login("nv_chuyen")

        res = self.client.get("/api/users/")
        self.assertEqual(res.status_code, 403)

    def test_03_chua_dang_nhap_bi_tu_choi(self):
        res = self.client.get("/api/users/")
        self.assertEqual(res.status_code, 401)
