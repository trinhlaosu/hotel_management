"""Run the booking E2E flow against the configured real database.

Ngoai HTTP status, file nay con xac minh gia tri cu the trong response:
  - Khach hang, booking duoc tao dung field.
  - Hoa don tinh dung: room_charge, service_charge, total.
  - Trang thai phong chuyen dung qua tung buoc.
  - Thanh toan ghi dung payment_method, paid_at.

Kich ban:
  1. Le tan dang nhap, tao khach hang, dat phong, confirm, check-in.
  2. Them dich vu → CHECK hoa don cap nhat (service_charge, total).
  3. Cap nhat so luong dich vu → CHECK hoa don cap nhat lan 2.
  4. Check-out → thanh toan → CHECK trang thai + so tien.
  5. Thu thanh toan lan 2 → phai bi tu choi (400).
  6. Scenario phu: tao booking → huy → xac minh phong ve trang thai trong.
  7. Quan ly dang nhap, xem bao cao.
  8. DB verification cuoi flow.

Usage:
    python hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py
    python hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py --prefix demo01
"""

import argparse
import html
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import Client

from hotel_app.models import (
    Booking, BookingService, Customer, Department, Employee, Invoice, Room,
    RoomType, Service, User,
)

# Gia tri data mau dung lam nen khi check so lieu
_ROOM_PRICE = 500_000    # Standard price_per_night
_SVC_PRICE  = 150_000    # An sang buffet price
_NIGHTS     = 3          # 2029-02-10 → 2029-02-13
_SVC_QTY_1  = 2
_SVC_QTY_2  = 3
_SVC_SUB_1  = _SVC_PRICE * _SVC_QTY_1   # 300_000
_SVC_SUB_2  = _SVC_PRICE * _SVC_QTY_2   # 450_000


class BookingFlowDbRunner:
    def __init__(self, prefix=None):
        self.client = Client(enforce_csrf_checks=False)
        self.prefix = prefix or datetime.now().strftime("book%H%M%S")
        self.rows = []
        self.report_path = (
            Path(__file__).resolve().parent / "bao_cao_e2e_booking_flow.html"
        )

    # ── Runner ────────────────────────────────────────────────────────────────

    def run(self):
        self._prepare_data()
        self._run_flow()
        self._write_report()

        failed = [row for row in self.rows if not row["passed"]]
        if failed:
            print(f"Co {len(failed)} buoc FAIL. Xem {self.report_path}")
            raise SystemExit(1)
        print(f"Da chay booking flow tren DB thanh cong. Xem {self.report_path}")

    # ── Seed data (upsert de chay nhieu lan khong bi loi) ─────────────────────

    def _prepare_data(self):
        self.manager = User.all_objects.update_or_create(
            username="ql001",
            defaults={
                "password": make_password("MyChi@123"),
                "email": "mychi@hotel.vn",
                "role": "quan_ly",
                "is_active": True,
                "is_deleted": False,
            },
        )[0]
        self.receptionist = User.all_objects.update_or_create(
            username="lt001",
            defaults={
                "password": make_password("Chuyen@123"),
                "email": "chuyen@hotel.vn",
                "role": "le_tan",
                "is_active": True,
                "is_deleted": False,
            },
        )[0]
        self.department = Department.all_objects.get_or_create(
            name="Le tan",
            defaults={
                "description": "Tiep nhan khach, tao dat phong, check-in, check-out",
                "is_deleted": False,
            },
        )[0]
        self.employee = Employee.all_objects.update_or_create(
            user=self.receptionist,
            defaults={
                "department": self.department,
                "full_name": "Vo Mong Chuyen",
                "phone": "0901000002",
                "salary": 9000000,
                "hire_date": "2024-02-15",
                "shift": "sang",
                "status": "dang_lam",
                "is_deleted": False,
            },
        )[0]
        self.room_type = RoomType.all_objects.get_or_create(
            name="Standard",
            defaults={
                "price_per_night": 500000,
                "capacity": 2,
                "description": "Phong tieu chuan, phu hop khach luu tru ngan ngay",
                "is_deleted": False,
            },
        )[0]
        # Dam bao phong 104 o trang thai trong truoc khi chay
        self.room = Room.all_objects.update_or_create(
            room_number="104",
            defaults={
                "room_type": self.room_type,
                "floor": 1,
                "status": "trong",
                "is_deleted": False,
            },
        )[0]
        self.service = Service.all_objects.update_or_create(
            name="An sang buffet",
            defaults={
                "price": 150000,
                "description": "Buffet sang tu 6h30 den 9h30",
                "is_active": True,
                "is_deleted": False,
            },
        )[0]

    # ── HTTP helper ───────────────────────────────────────────────────────────

    def _api(self, group, action, method, url, expected=200, data=None, note=""):
        try:
            fn = {
                "GET":    lambda: self.client.get(url),
                "POST":   lambda: self.client.post(
                    url, data=json.dumps(data or {}),
                    content_type="application/json"),
                "PUT":    lambda: self.client.put(
                    url, data=json.dumps(data or {}),
                    content_type="application/json"),
                "PATCH":  lambda: self.client.patch(
                    url, data=json.dumps(data or {}),
                    content_type="application/json"),
                "DELETE": lambda: self.client.delete(
                    url, content_type="application/json"),
            }.get(method)
            if fn is None:
                raise ValueError(f"Unsupported method: {method}")
            response = fn()
        except Exception as exc:
            self.rows.append({
                "group": group, "action": action, "method": method,
                "url": url, "expected": expected,
                "actual": "EXCEPTION", "passed": False,
                "note": note or str(exc),
            })
            return {}

        actual = response.status_code
        expected_values = expected if isinstance(expected, (list, tuple)) else [expected]
        passed = actual in expected_values
        body = {}
        try:
            body = response.json()
        except ValueError:
            pass
        if not note and isinstance(body, dict):
            note = body.get("message") or body.get("error") or ""
        self.rows.append({
            "group": group, "action": action, "method": method,
            "url": url, "expected": expected,
            "actual": actual, "passed": passed, "note": note,
        })
        return body

    def _db_check(self, action, ok, note=""):
        self.rows.append({
            "group": "DB", "action": action, "method": "CHECK",
            "url": "hotel_management DB",
            "expected": True, "actual": ok,
            "passed": ok is True,
            "note": note or "Kiem tra truc tiep DB that",
        })

    def _g(self, body, *path):
        """Safe-get: navigate nested dict, return None if missing."""
        cur = body
        for key in path:
            if isinstance(cur, dict):
                cur = cur.get(key)
            else:
                return None
        return cur

    def _num(self, body, *path):
        """Get numeric value from body path. Returns None if not parseable."""
        val = self._g(body, *path)
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    def _check(self, group, action, ok, note=""):
        """Record a data-validation row (not an HTTP call)."""
        self.rows.append({
            "group": group, "action": action,
            "method": "CHECK", "url": "-",
            "expected": True, "actual": ok,
            "passed": ok is True, "note": note,
        })

    def _safe_id(self, body, *keys):
        """Lay id tu response body an toan, khong raise exception."""
        data = body.get("data") if isinstance(body, dict) else {}
        if not isinstance(data, dict):
            return None
        for key in keys:
            val = data.get(key)
            if val is not None:
                return val
        return None

    def _logout(self):
        self.client.post("/api/auth/logout/", content_type="application/json")

    # ── Main flow ─────────────────────────────────────────────────────────────

    def _run_flow(self):
        # ── BUOC 1: Le tan dang nhap ──────────────────────────────────────────
        self._api("Auth", "Le tan dang nhap", "POST", "/api/auth/login/", 200, {
            "username": self.receptionist.username,
            "password": "Chuyen@123",
        })

        # ── BUOC 2: Kiem tra phong trong ──────────────────────────────────────
        room_list = self._api("Rooms", "Xem danh sach phong trong", "GET",
                              "/api/rooms/?status=trong")
        self._check("Rooms", "Danh sach phong trong tra ve list",
                    isinstance(self._g(room_list, "data"), list))

        room_detail = self._api("Rooms", "Xem chi tiet phong 104", "GET",
                                f"/api/rooms/{self.room.id}/")
        self._check("Rooms", "Phong 104 dang o trang thai trong",
                    self._g(room_detail, "data", "status") == "trong")
        self._check("Rooms", "Phong 104 o tang 1",
                    self._g(room_detail, "data", "floor") == 1)

        # ── BUOC 3: Tao khach hang ────────────────────────────────────────────
        customer_body = self._api(
            "Customers", "Tao khach hang moi", "POST", "/api/customers/", 201, {
                "full_name": f"Nguyen Tat Hung E2E {self.prefix}",
                "phone": self._phone(2),
                "email": f"nguyentathung.e2e.{self.prefix}@gmail.com",
                "id_card": self._id_card(),
                "address": "Quan Phu Nhuan, TP. Ho Chi Minh",
                "customer_type": "regular",
            }, "Insert Customer: Nguyen Tat Hung, loai regular",
        )
        customer_id = self._safe_id(customer_body, "id")
        self._check("Customers", "customer_id duoc tra ve", customer_id is not None)
        self._check("Customers", "Customer.customer_type = regular",
                    self._g(customer_body, "data", "customer_type") == "regular")

        cust_detail = self._api("Customers", "Xem chi tiet khach hang vua tao", "GET",
                                f"/api/customers/{customer_id}/")
        self._check("Customers", "Customer detail tra ve dung id",
                    self._g(cust_detail, "data", "id") == customer_id)

        # ── BUOC 4: Dat phong ─────────────────────────────────────────────────
        booking_body = self._api(
            "Bookings", "Tao dat phong", "POST", "/api/bookings/", 201, {
                "customer_id": customer_id,
                "room_id": self.room.id,
                "check_in": "2029-02-10",
                "check_out": "2029-02-13",
                "note": f"Booking flow E2E {self.prefix}",
            }, f"{_NIGHTS} dem (10/02 → 13/02), phong 104 Standard {_ROOM_PRICE:,}/dem",
        )
        booking_id = self._safe_id(booking_body, "booking_id", "id")
        self._check("Bookings", "booking_id duoc tra ve", booking_id is not None)
        self._check("Bookings", "Booking.tong_tien > 0 sau tao",
                    (self._num(booking_body, "data", "tong_tien") or 0) > 0)

        bk_detail = self._api("Bookings", "Xem chi tiet booking vua tao", "GET",
                              f"/api/bookings/{booking_id}/")
        self._check("Bookings", f"Booking.so_dem = {_NIGHTS}",
                    self._num(bk_detail, "data", "so_dem") == _NIGHTS,
                    "2029-02-10 → 2029-02-13 = 3 dem")
        self._check("Bookings", "Booking.tien_phong > 0",
                    (self._num(bk_detail, "data", "tien_phong") or 0) > 0)

        # ── BUOC 5: Tinh gia du kien ──────────────────────────────────────────
        pr_body = self._api(
            "Pricing", "Tinh gia booking du kien (regular)", "POST",
            "/api/pricing/calculate-booking-price/", 200, {
                "room_id": self.room.id,
                "check_in": "2029-02-10",
                "check_out": "2029-02-13",
                "customer_type": "regular",
            },
        )
        self._check("Pricing", f"Pricing.so_dem = {_NIGHTS}",
                    self._num(pr_body, "data", "so_dem") == _NIGHTS,
                    "2029-02-10 → 2029-02-13 = 3 dem")
        self._check("Pricing", "Pricing.final_price > 0",
                    (self._num(pr_body, "data", "final_price") or 0) > 0)

        # ── BUOC 6: Xac nhan dat phong ────────────────────────────────────────
        self._api("Bookings", "Xac nhan dat phong (confirm)", "PUT",
                  f"/api/bookings/{booking_id}/confirm/",
                  note="cho_xac_nhan → da_xac_nhan")

        self._api("Bookings", "Thu xac nhan lan 2 (phai fail 400)", "PUT",
                  f"/api/bookings/{booking_id}/confirm/", 400,
                  note="Da xac nhan roi, khong the xac nhan lai")

        # ── BUOC 7: Check-in ──────────────────────────────────────────────────
        self._api("Bookings", "Check-in (da_xac_nhan → dang_o)", "PUT",
                  f"/api/bookings/{booking_id}/check-in/")

        room_after_checkin = self._api(
            "Rooms", "Kiem tra phong 104 sau check-in", "GET",
            f"/api/rooms/{self.room.id}/")
        self._check("Rooms", "Phong 104 chuyen sang co_khach sau check-in",
                    self._g(room_after_checkin, "data", "status") == "co_khach")

        # ── BUOC 8: Xem hoa don ngay sau check-in (chua co dich vu) ──────────
        invoice_body_init = self._api(
            "Invoices", "Xem hoa don sau check-in (chua dich vu)", "GET",
            f"/api/bookings/{booking_id}/invoice/",
        )
        invoice_id = self._safe_id(invoice_body_init, "id")
        self._check("Invoices", "invoice_id duoc tra ve", invoice_id is not None)
        self._check("Invoices", "room_charge > 0 ngay sau check-in",
                    (self._num(invoice_body_init, "data", "room_charge") or 0) > 0)
        self._check("Invoices", "service_charge = 0 khi chua co dich vu",
                    self._num(invoice_body_init, "data", "service_charge") == 0)
        self._check("Invoices", "payment_status = chua_thanh_toan sau check-in",
                    self._g(invoice_body_init, "data", "payment_status") == "chua_thanh_toan")
        room_charge = self._num(invoice_body_init, "data", "room_charge") or 0

        inv_full = self._api("Invoices", "Xem hoa don full detail qua /api/invoices/", "GET",
                             f"/api/invoices/{invoice_id}/")
        self._check("Invoices", "Invoice detail tra ve dung id",
                    self._g(inv_full, "data", "id") == invoice_id)
        self._check("Invoices", "Invoice.paid_at = null truoc khi thanh toan",
                    self._g(inv_full, "data", "paid_at") is None)

        # ── BUOC 9: Them dich vu lan 1 (qty=2) ───────────────────────────────
        svc_body = self._api(
            "Booking services",
            f"Them dich vu: An sang buffet (qty={_SVC_QTY_1})", "POST",
            f"/api/bookings/{booking_id}/services/", 201, {
                "service_id": self.service.id,
                "quantity": _SVC_QTY_1,
            }, f"{_SVC_QTY_1} x {_SVC_PRICE:,} = {_SVC_SUB_1:,}",
        )
        booking_service_id = self._safe_id(svc_body, "id")
        self._check("Booking services", "BookingService.id duoc tra ve",
                    booking_service_id is not None)
        self._check("Booking services",
                    f"BookingService.quantity = {_SVC_QTY_1}",
                    self._g(svc_body, "data", "quantity") == _SVC_QTY_1)
        self._check("Booking services",
                    f"BookingService.subtotal = {_SVC_SUB_1:,} ({_SVC_QTY_1} x {_SVC_PRICE:,})",
                    self._num(svc_body, "data", "subtotal") == _SVC_SUB_1)

        svc_list = self._api("Booking services", "Danh sach dich vu theo booking", "GET",
                             f"/api/bookings/{booking_id}/services/")
        self._check("Booking services", "List booking-services tra ve list",
                    isinstance(self._g(svc_list, "data"), list))
        self._check("Booking services", "Booking co it nhat 1 dich vu",
                    len(self._g(svc_list, "data") or []) >= 1)

        inv_after_add = self._api(
            "Invoices",
            f"Kiem tra hoa don sau them dich vu (qty={_SVC_QTY_1})", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices",
                    f"service_charge = {_SVC_SUB_1:,} sau qty={_SVC_QTY_1}",
                    self._num(inv_after_add, "data", "service_charge") == _SVC_SUB_1,
                    f"{_SVC_QTY_1} x {_SVC_PRICE:,} = {_SVC_SUB_1:,}")
        self._check("Invoices",
                    f"total = room_charge + {_SVC_SUB_1:,}",
                    self._num(inv_after_add, "data", "total") == room_charge + _SVC_SUB_1,
                    f"{room_charge:,.0f} + {_SVC_SUB_1:,} = {room_charge + _SVC_SUB_1:,.0f}")

        # ── BUOC 10: Cap nhat so luong dich vu (qty 2 → 3) ───────────────────
        self._api(
            "Booking services",
            f"Cap nhat so luong dich vu (qty={_SVC_QTY_2})", "PUT",
            f"/api/booking-services/{booking_service_id}/", 200,
            {"quantity": _SVC_QTY_2},
            f"{_SVC_QTY_2} x {_SVC_PRICE:,} = {_SVC_SUB_2:,}",
        )

        inv_after_upd = self._api(
            "Invoices",
            f"Kiem tra hoa don sau cap nhat dich vu (qty={_SVC_QTY_2})", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices",
                    f"service_charge = {_SVC_SUB_2:,} sau qty={_SVC_QTY_2}",
                    self._num(inv_after_upd, "data", "service_charge") == _SVC_SUB_2,
                    f"{_SVC_QTY_2} x {_SVC_PRICE:,} = {_SVC_SUB_2:,}")
        self._check("Invoices",
                    f"total = room_charge + {_SVC_SUB_2:,}",
                    self._num(inv_after_upd, "data", "total") == room_charge + _SVC_SUB_2,
                    f"{room_charge:,.0f} + {_SVC_SUB_2:,} = {room_charge + _SVC_SUB_2:,.0f}")

        # ── BUOC 11: Check-out ────────────────────────────────────────────────
        self._api("Bookings", "Check-out (dang_o → da_tra_phong)", "PUT",
                  f"/api/bookings/{booking_id}/check-out/")

        # ── BUOC 12: Xem hoa don cuoi (sau check-out) ────────────────────────
        self._api(
            "Invoices", "Xem hoa don cuoi qua booking (sau check-out)", "GET",
            f"/api/bookings/{booking_id}/invoice/",
        )

        inv_pre_pay = self._api(
            "Invoices", "Xem hoa don cuoi full detail (chua thanh toan)", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices", "payment_status = chua_thanh_toan truoc thanh toan",
                    self._g(inv_pre_pay, "data", "payment_status") == "chua_thanh_toan")
        self._check("Invoices", "paid_at = null truoc thanh toan",
                    self._g(inv_pre_pay, "data", "paid_at") is None)
        self._check("Invoices", "total > 0 sau check-out",
                    (self._num(inv_pre_pay, "data", "total") or 0) > 0)
        self._check("Invoices",
                    f"total = room_charge + {_SVC_SUB_2:,} (cuoi cung)",
                    self._num(inv_pre_pay, "data", "total") == room_charge + _SVC_SUB_2)

        room_after_checkout = self._api(
            "Rooms", "Kiem tra phong 104 ve trong sau check-out", "GET",
            f"/api/rooms/{self.room.id}/")
        self._check("Rooms", "Phong 104 ve trang thai trong sau check-out",
                    self._g(room_after_checkout, "data", "status") == "trong")

        # ── BUOC 13: Thanh toan hoa don ──────────────────────────────────────
        pay_body = self._api(
            "Invoices", "Thanh toan hoa don (chuyen_khoan)", "PUT",
            f"/api/invoices/{invoice_id}/pay/", 200,
            {"payment_method": "chuyen_khoan"},
        )
        self._check("Invoices", "payment_status = da_thanh_toan sau thanh toan",
                    self._g(pay_body, "data", "payment_status") == "da_thanh_toan")
        self._check("Invoices", "payment_method = chuyen_khoan",
                    self._g(pay_body, "data", "payment_method") == "chuyen_khoan")
        self._check("Invoices", "paid_at khong null sau thanh toan",
                    self._g(pay_body, "data", "paid_at") is not None)
        self._check("Invoices", "total khong doi sau thanh toan",
                    self._num(pay_body, "data", "total") == room_charge + _SVC_SUB_2,
                    "So tien phai giu nguyen sau khi thanh toan")

        # ── BUOC 14: Xac minh hoa don sau thanh toan ─────────────────────────
        inv_paid = self._api(
            "Invoices", "Xem hoa don sau thanh toan (GET full detail)", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices", "payment_status = da_thanh_toan (GET xac nhan)",
                    self._g(inv_paid, "data", "payment_status") == "da_thanh_toan")
        self._check("Invoices", "payment_method = chuyen_khoan (GET xac nhan)",
                    self._g(inv_paid, "data", "payment_method") == "chuyen_khoan")
        self._check("Invoices", "paid_at duoc luu (GET xac nhan)",
                    self._g(inv_paid, "data", "paid_at") is not None)

        # ── BUOC 15: Thu thanh toan lan 2 (phai bi tu choi) ──────────────────
        self._api(
            "Invoices", "Thu thanh toan lan 2 (phai fail 400)", "PUT",
            f"/api/invoices/{invoice_id}/pay/", 400,
            {"payment_method": "tien_mat"},
            "Da thanh toan roi, khong the thanh toan lai",
        )

        # ── SCENARIO PHU: Tao booking → huy → xac minh ───────────────────────
        cancel_body = self._api(
            "Bookings", "[Scenario huy] Tao booking moi de huy", "POST",
            "/api/bookings/", 201, {
                "customer_id": customer_id,
                "room_id": self.room.id,
                "check_in": "2030-06-01",
                "check_out": "2030-06-03",
                "note": f"Booking se huy E2E {self.prefix}",
            }, "Booking nay se bi huy ngay sau do",
        )
        cancel_booking_id = self._safe_id(cancel_body, "booking_id", "id")
        self._check("Bookings", "[Scenario huy] cancel_booking_id duoc tra ve",
                    cancel_booking_id is not None)

        self._api("Bookings", "[Scenario huy] Huy dat phong", "PUT",
                  f"/api/bookings/{cancel_booking_id}/cancel/",
                  note="cho_xac_nhan → da_huy")

        cancel_detail = self._api(
            "Bookings", "[Scenario huy] Xem chi tiet booking da huy", "GET",
            f"/api/bookings/{cancel_booking_id}/")
        self._check("Bookings", "[Scenario huy] status = da_huy",
                    self._g(cancel_detail, "data", "status") == "da_huy")

        room_after_cancel = self._api(
            "Rooms", "[Scenario huy] Kiem tra phong ve trong sau huy", "GET",
            f"/api/rooms/{self.room.id}/")
        self._check("Rooms", "[Scenario huy] Phong ve trang thai trong sau huy",
                    self._g(room_after_cancel, "data", "status") == "trong")

        # ── BUOC 16: Le tan dang xuat ─────────────────────────────────────────
        self._api("Auth", "Le tan dang xuat", "POST", "/api/auth/logout/")

        # ── BUOC 17: Quan ly dang nhap, xem bao cao ──────────────────────────
        self._api("Auth", "Quan ly dang nhap", "POST", "/api/auth/login/", 200, {
            "username": self.manager.username,
            "password": "MyChi@123",
        })

        self._api("Reports", "Bao cao doanh thu (tat ca)", "GET",
                  "/api/reports/revenue/")
        self._api("Reports", "Bao cao dat phong (tat ca)", "GET",
                  "/api/reports/booking-statistics/")
        self._api("Reports", "Bao cao trang thai phong", "GET",
                  "/api/reports/room-status/")
        self._api("Reports", "Top 5 dich vu su dung nhieu nhat", "GET",
                  "/api/reports/top-services/?top=5")

        self._api("Invoices", "Quan ly xem danh sach hoa don", "GET",
                  "/api/invoices/")
        self._api("Invoices", "Quan ly loc hoa don da thanh toan", "GET",
                  "/api/invoices/?payment_status=da_thanh_toan")
        self._api("Invoices", "Quan ly loc hoa don chuyen_khoan", "GET",
                  "/api/invoices/?payment_method=chuyen_khoan")

        self._api("Auth", "Quan ly dang xuat", "POST", "/api/auth/logout/")

        # Kiem tra unauthenticated sau khi dang xuat
        self._api("Auth", "Chan truy cap khi chua dang nhap (invoices)", "GET",
                  "/api/invoices/", 401)
        self._api("Auth", "Chan truy cap khi chua dang nhap (reports)", "GET",
                  "/api/reports/revenue/", 401)

        # ── DB VERIFICATION ───────────────────────────────────────────────────
        self._db_check(
            "Booking chinh da tra phong",
            Booking.all_objects.filter(id=booking_id, status="da_tra_phong").exists(),
            "Booking ton tai tren DB voi status=da_tra_phong",
        )
        self._db_check(
            "Phong 104 ve trang thai trong",
            Room.all_objects.filter(id=self.room.id, status="trong").exists(),
            "Phong duoc mo lai sau check-out",
        )
        self._db_check(
            "BookingService da duoc luu",
            BookingService.all_objects.filter(booking_id=booking_id).exists(),
            "Dich vu su dung duoc luu tren DB",
        )
        self._db_check(
            "BookingService co so luong = 3",
            BookingService.all_objects.filter(
                id=booking_service_id, quantity=3).exists(),
            "So luong dich vu da duoc cap nhat thanh 3",
        )
        self._db_check(
            "Invoice da thanh toan",
            Invoice.all_objects.filter(
                id=invoice_id, payment_status="da_thanh_toan").exists(),
            "Invoice payment_status=da_thanh_toan tren DB",
        )
        self._db_check(
            "Invoice phuong thuc chuyen_khoan",
            Invoice.all_objects.filter(
                id=invoice_id, payment_method="chuyen_khoan").exists(),
            "Invoice payment_method=chuyen_khoan tren DB",
        )
        self._db_check(
            "Invoice da co paid_at",
            Invoice.all_objects.filter(
                id=invoice_id, paid_at__isnull=False).exists(),
            "paid_at duoc set sau khi thanh toan",
        )
        self._db_check(
            "Customer da tao",
            Customer.all_objects.filter(id=customer_id).exists(),
            "Khach hang ton tai tren DB",
        )
        self._db_check(
            "Booking huy da co status da_huy",
            Booking.all_objects.filter(
                id=cancel_booking_id, status="da_huy").exists(),
            "Booking huy co status=da_huy tren DB",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _phone(self, index):
        tail = "".join(ch for ch in self.prefix if ch.isdigit())[-7:].rjust(7, "0")
        return f"09{tail}{index}"[:15]

    def _id_card(self):
        tail = "".join(ch for ch in self.prefix if ch.isdigit())[-6:].rjust(6, "0")
        return f"079206{tail}55"

    # ── HTML report ───────────────────────────────────────────────────────────

    def _write_report(self):
        total = len(self.rows)
        passed = sum(1 for row in self.rows if row["passed"])
        failed = total - passed
        generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        groups: dict = {}
        for row in self.rows:
            g = row["group"]
            if g not in groups:
                groups[g] = {"total": 0, "passed": 0}
            groups[g]["total"] += 1
            if row["passed"]:
                groups[g]["passed"] += 1

        group_summary_html = "\n".join(
            f"""<tr>
              <td>{g}</td>
              <td>{info['total']}</td>
              <td style="color:#047857;font-weight:700">{info['passed']}</td>
              <td style="color:#b91c1c;font-weight:700">{info['total'] - info['passed']}</td>
            </tr>"""
            for g, info in groups.items()
        )

        rows_html = "\n".join(
            f"""
            <tr class="{ 'pass' if row['passed'] else 'fail' }{ ' check-row' if row['method'] == 'CHECK' else '' }">
              <td>{index}</td>
              <td>{html.escape(row['group'])}</td>
              <td>{html.escape(row['action'])}</td>
              <td><code>{html.escape(row['method'])}</code></td>
              <td><code>{html.escape(row['url'])}</code></td>
              <td>{html.escape(str(row['expected']))}</td>
              <td>{html.escape(str(row['actual']))}</td>
              <td>{'PASS' if row['passed'] else 'FAIL'}</td>
              <td>{html.escape(str(row['note']))}</td>
            </tr>
            """
            for index, row in enumerate(self.rows, start=1)
        )

        content = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Báo cáo Kiểm thử E2E – Luồng Đặt phòng &amp; Thanh toán – Nhóm 04</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2933; }}
    header {{ padding: 24px 36px; background: #f7f9fc; border-bottom: 2px solid #d8dee8; }}
    main {{ padding: 24px 36px 36px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    h2 {{ margin: 24px 0 10px; font-size: 18px; color: #374151; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; margin: 18px 0 24px; }}
    .box {{ border: 1px solid #d8dee8; padding: 12px; }}
    .label {{ color: #637083; font-size: 13px; }}
    .value {{ font-weight: 700; font-size: 20px; }}
    .value.ok {{ color: #047857; }}
    .value.ng {{ color: #b91c1c; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 28px; }}
    th, td {{ border: 1px solid #d8dee8; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
    tr.pass td:nth-child(8) {{ color: #047857; font-weight: 700; }}
    tr.fail td:nth-child(8) {{ color: #b91c1c; font-weight: 700; }}
    tr.check-row {{ background: #fafafa; }}
    tr.check-row td:nth-child(4) code {{ background: #e0f2fe; color: #0369a1; }}
    code {{ background: #f5f7fa; padding: 1px 4px; border-radius: 4px; font-size: 12px; }}
    .scenario {{ background:#fffbeb; border-left:4px solid #f59e0b; padding:10px 14px; margin:16px 0; font-size:13px; }}
  </style>
</head>
<body>
  <header>
    <h1>Báo cáo Kiểm thử E2E – Luồng Đặt phòng &amp; Thanh toán – Nhóm 04</h1>
    <div>Thời gian sinh báo cáo: {generated_at}</div>
    <div>Database: <code>{settings.DATABASES['default']['NAME']}</code></div>
    <div>Prefix dữ liệu: <code>{html.escape(self.prefix)}</code></div>
  </header>
  <main>
    <div class="scenario">
      <strong>Kịch bản kiểm thử:</strong>
      Lễ tân đăng nhập → Tạo khách hàng → Đặt phòng → Xác nhận → Check-in →
      Thêm dịch vụ → Cập nhật số lượng dịch vụ → Check-out → <strong>Thanh toán</strong> →
      Xác minh hóa đơn đã thanh toán → Thử thanh toán lại (phải bị từ chối) →
      Kịch bản hủy đặt phòng → Quản lý xem báo cáo → DB verification.
    </div>

    <section class="summary">
      <div class="box">
        <div class="label">Trạng thái</div>
        <div class="value {'ok' if failed == 0 else 'ng'}">{'PASS' if failed == 0 else 'FAIL'}</div>
      </div>
      <div class="box"><div class="label">Tổng bước</div><div class="value">{total}</div></div>
      <div class="box"><div class="label">PASS</div><div class="value ok">{passed}</div></div>
      <div class="box"><div class="label">FAIL</div><div class="value ng">{failed}</div></div>
    </section>

    <h2>Tổng hợp theo nhóm</h2>
    <table style="width:auto">
      <thead>
        <tr><th>Nhóm</th><th>Tổng</th><th>PASS</th><th>FAIL</th></tr>
      </thead>
      <tbody>{group_summary_html}</tbody>
    </table>

    <h2>Chi tiết từng bước</h2>
    <table>
      <thead>
        <tr>
          <th>#</th><th>Nhóm</th><th>Action</th><th>Method</th>
          <th>API / DB</th><th>Expected</th><th>Actual</th>
          <th>Kết quả</th><th>Ghi chú</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </main>
</body>
</html>
"""
        self.report_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Chay booking flow E2E tren database that."
    )
    parser.add_argument(
        "--prefix", default=None,
        help="Tien to du lieu sinh ra, vi du: demo01",
    )
    args = parser.parse_args()
    BookingFlowDbRunner(prefix=args.prefix).run()


if __name__ == "__main__":
    main()
