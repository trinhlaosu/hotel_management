"""End-to-end tests for the main hotel workflow."""

from hotel_app.models import Booking, BookingService, Invoice, Room

from ..view_test_base import BaseTest


class BookingFlowE2ETest(BaseTest):
    def test_e2e_booking_service_invoice_payment_report_flow(self):
        login_res = self.login("nv_chuyen")
        self.assertEqual(login_res.status_code, 200)

        rooms_res = self.client.get("/api/rooms/?status=trong")
        self.assertEqual(rooms_res.status_code, 200)
        self.assertTrue(
            any(room["id"] == self.room.id for room in rooms_res.json()["data"])
        )

        customer_res = self.post("/api/customers/", {
            "full_name": "Khach Hang E2E",
            "phone": "0911222333",
            "email": "e2e.customer@hotel.vn",
            "id_card": "079206099999",
            "address": "TP. Ho Chi Minh",
            "customer_type": "regular",
        })
        self.assertEqual(customer_res.status_code, 201)
        customer_id = customer_res.json()["data"]["id"]

        booking_res = self.post("/api/bookings/", {
            "customer_id": customer_id,
            "room_id": self.room.id,
            "check_in": "2028-08-10",
            "check_out": "2028-08-13",
            "note": "E2E booking",
        })
        self.assertEqual(booking_res.status_code, 201)
        booking_id = booking_res.json()["data"]["booking_id"]
        self.assertTrue(Invoice.objects.filter(booking_id=booking_id).exists())

        confirm_res = self.put(f"/api/bookings/{booking_id}/confirm/")
        self.assertEqual(confirm_res.status_code, 200)
        self.assertEqual(confirm_res.json()["data"]["status"], "da_xac_nhan")

        check_in_res = self.put(f"/api/bookings/{booking_id}/check-in/")
        self.assertEqual(check_in_res.status_code, 200)
        self.assertEqual(check_in_res.json()["data"]["status"], "dang_o")
        room = Room.objects.get(id=self.room.id)
        self.assertEqual(room.status, "co_khach")

        service_res = self.post(f"/api/bookings/{booking_id}/services/", {
            "service_id": self.service.id,
            "quantity": 2,
        })
        self.assertEqual(service_res.status_code, 201)
        self.assertTrue(
            BookingService.objects.filter(booking_id=booking_id).exists()
        )
        invoice = Invoice.objects.get(booking_id=booking_id)
        self.assertEqual(float(invoice.service_charge), 300000.0)
        self.assertEqual(float(invoice.total), 1800000.0)

        check_out_res = self.put(f"/api/bookings/{booking_id}/check-out/")
        self.assertEqual(check_out_res.status_code, 200)
        self.assertEqual(check_out_res.json()["data"]["status"], "da_tra_phong")
        room.refresh_from_db()
        self.assertEqual(room.status, "trong")

        invoice_res = self.client.get(f"/api/bookings/{booking_id}/invoice/")
        self.assertEqual(invoice_res.status_code, 200)
        invoice_id = invoice_res.json()["data"]["id"]
        self.assertEqual(float(invoice_res.json()["data"]["total"]), 1800000.0)

        pay_res = self.put(f"/api/invoices/{invoice_id}/pay/", {
            "payment_method": "chuyen_khoan",
        })
        self.assertEqual(pay_res.status_code, 200)
        self.assertEqual(pay_res.json()["data"]["payment_status"], "da_thanh_toan")

        self.client.post("/api/auth/logout/", content_type="application/json")
        admin_login_res = self.login("admin_mychi")
        self.assertEqual(admin_login_res.status_code, 200)

        revenue_res = self.client.get("/api/reports/revenue/")
        self.assertEqual(revenue_res.status_code, 200)
        self.assertEqual(revenue_res.json()["data"]["so_hoa_don_da_tt"], 1)
        self.assertEqual(revenue_res.json()["data"]["tong_doanh_thu"], 1800000.0)

        booking = Booking.objects.get(id=booking_id)
        self.assertEqual(booking.status, "da_tra_phong")
