"""View API tests."""

from hotel_app.models import Customer, Room, RoomType

from ..view_test_base import BaseTest


class CustomerTest(BaseTest):


    def test_04_xem_danh_sach_khach_hang(self):
        self.login()

        res = self.client.get("/api/customers/")

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["data"], list)

    def test_04_loc_khach_vip(self):
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
        self.login()

        res = self.client.get("/api/customers/?phone=0909090901")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertGreaterEqual(len(ds), 1)
        phones = [kh["phone"] for kh in ds]
        self.assertTrue(any("0909090901" in p for p in phones))


    def test_05_them_khach_hang_moi(self):
        self.login()

        res = self.post("/api/customers/", {
            "full_name": "Tran Thi Moi",
            "phone":     "0777777777",
            "id_card":   "777777777777",
        })

        self.assertEqual(res.status_code, 201)
        self.assertTrue(Customer.objects.filter(phone="0777777777").exists())

    def test_05_them_khach_trung_cccd(self):
        self.login()

        res = self.post("/api/customers/", {
            "full_name": "Nguoi Khac",
            "phone":     "0666666666",
            "id_card":   "012345678901",
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_05_them_khach_thieu_truong_bat_buoc(self):
        self.login()

        res = self.post("/api/customers/", {
            "full_name": "Thieu CCCD",
            "phone":     "0555555555",
        })

        self.assertEqual(res.status_code, 400)


class RoomTest(BaseTest):


    def test_06_xem_danh_sach_phong(self):
        self.login()

        res = self.client.get("/api/rooms/")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertIsInstance(ds, list)
        self.assertGreaterEqual(len(ds), 1)
        phong = ds[0]
        for field in ["id", "room_number", "status", "room_type", "price_per_night"]:
            self.assertIn(field, phong)


    def test_07_loc_phong_con_trong(self):
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

    def test_07_loc_phong_theo_tang_va_suc_chua(self):
        room_type_4 = RoomType.objects.create(
            name="Family",
            price_per_night=900_000,
            capacity=4,
        )
        Room.objects.create(
            room_type=room_type_4,
            room_number="301",
            floor=3,
            status="trong",
        )
        self.login()

        res = self.client.get("/api/rooms/?floor=3&capacity=4")

        self.assertEqual(res.status_code, 200)
        ds = res.json()["data"]
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]["room_number"], "301")


    def test_08_cap_nhat_trang_thai_phong(self):
        self.login()

        res = self.put(f"/api/rooms/{self.room.id}/status/", {
            "status": "bao_tri",
        })

        self.assertEqual(res.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "bao_tri")

    def test_08_cap_nhat_trang_thai_thieu_status(self):
        self.login()

        res = self.put(f"/api/rooms/{self.room.id}/status/", {})

        self.assertEqual(res.status_code, 400)
