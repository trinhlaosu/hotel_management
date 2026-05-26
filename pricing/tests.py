from datetime import date

from hotel_app.tests.view_test_base import BaseTest
from pricing.services import BookingPriceCalculator


class PricingApiTest(BaseTest):
    def test_receptionist_calculates_booking_price(self):
        self.login("nv_chuyen")
        res = self.post("/api/pricing/calculate-booking-price/", {
            "room_id": self.room.id,
            "check_in": "2026-07-03",
            "check_out": "2026-07-06",
            "customer_type": "vip",
        })

        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertEqual(data["room_id"], self.room.id)
        self.assertEqual(data["so_dem"], 3)
        self.assertEqual(data["weekend_nights"], 2)
        self.assertEqual(data["base_price"], 1500000.0)
        self.assertEqual(data["weekend_fee"], 100000.0)
        self.assertEqual(data["vip_discount"], 160000.0)
        self.assertEqual(data["final_price"], 1440000.0)

    def test_guest_cannot_calculate_booking_price(self):
        res = self.post("/api/pricing/calculate-booking-price/", {
            "room_id": self.room.id,
            "check_in": "2026-07-03",
            "check_out": "2026-07-06",
            "customer_type": "regular",
        })

        self.assertEqual(res.status_code, 401)

    def test_calculator_returns_none_for_missing_room(self):
        room = BookingPriceCalculator().lay_phong(9999)

        self.assertIsNone(room)

    def test_calculator_regular_customer_has_no_vip_discount(self):
        data, err_msg = BookingPriceCalculator().tinh_gia(
            self.room,
            date(2026, 7, 6),
            date(2026, 7, 8),
            "regular",
        )

        self.assertIsNone(err_msg)
        self.assertEqual(data["so_dem"], 2)
        self.assertEqual(data["vip_discount"], 0.0)
        self.assertEqual(data["final_price"], 1000000.0)
