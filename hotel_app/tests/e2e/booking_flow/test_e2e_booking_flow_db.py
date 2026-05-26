"""Run the booking E2E flow against the configured real database.

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

from django.contrib.auth.hashers import make_password
from django.test import Client

from hotel_app.models import (
    Booking, BookingService, Customer, Department, Employee, Invoice, Room,
    RoomType, Service, User,
)


class BookingFlowDbRunner:
    def __init__(self, prefix=None):
        self.client = Client(enforce_csrf_checks=False)
        self.prefix = prefix or datetime.now().strftime("book%H%M%S")
        self.rows = []
        self.report_path = (
            Path(__file__).resolve().parent / "bao_cao_e2e_booking_flow.html"
        )

    def run(self):
        self._prepare_data()
        self._run_flow()
        self._write_report()

        failed = [row for row in self.rows if not row["passed"]]
        if failed:
            print(f"Co {len(failed)} buoc FAIL. Xem {self.report_path}")
            raise SystemExit(1)
        print(f"Da chay booking flow tren DB thanh cong. Xem {self.report_path}")

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
            },
        )[0]
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

    def _phone(self, index):
        tail = "".join(ch for ch in self.prefix if ch.isdigit())[-7:].rjust(7, "0")
        return f"09{tail}{index}"[:15]

    def _id_card(self):
        tail = "".join(ch for ch in self.prefix if ch.isdigit())[-6:].rjust(6, "0")
        return f"079206{tail}55"

    def _api(self, group, action, method, url, expected=200, data=None, note=""):
        if method == "GET":
            response = self.client.get(url)
        elif method == "POST":
            response = self.client.post(
                url,
                data=json.dumps(data or {}),
                content_type="application/json",
            )
        elif method == "PUT":
            response = self.client.put(
                url,
                data=json.dumps(data or {}),
                content_type="application/json",
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

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
            "group": group,
            "action": action,
            "method": method,
            "url": url,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "note": note,
        })
        return body

    def _db_check(self, action, ok, note):
        self.rows.append({
            "group": "DB",
            "action": action,
            "method": "CHECK",
            "url": "hotel_management",
            "expected": True,
            "actual": ok,
            "passed": ok is True,
            "note": note,
        })

    def _run_flow(self):
        self._api("Auth", "Dang nhap le tan", "POST", "/api/auth/login/", 200, {
            "username": self.receptionist.username,
            "password": "Chuyen@123",
        })
        self._api("Rooms", "Xem phong trong", "GET", "/api/rooms/?status=trong")

        customer_body = self._api(
            "Customers",
            "Tao khach hang",
            "POST",
            "/api/customers/",
            201,
            {
                "full_name": f"Nguyen Tat Hung E2E {self.prefix}",
                "phone": self._phone(2),
                "email": f"nguyentathung.e2e.{self.prefix}@gmail.com",
                "id_card": self._id_card(),
                "address": "Quan Phu Nhuan, TP. Ho Chi Minh",
                "customer_type": "regular",
            },
            "Insert Customer theo mau Nguyen Tat Hung",
        )
        customer_id = customer_body["data"]["id"]

        booking_body = self._api(
            "Bookings",
            "Tao dat phong",
            "POST",
            "/api/bookings/",
            201,
            {
                "customer_id": customer_id,
                "room_id": self.room.id,
                "check_in": "2029-02-10",
                "check_out": "2029-02-13",
                "note": f"Booking E2E map data mau {self.prefix}",
            },
            "Insert Booking bang le tan lt001, phong 104, loai Standard",
        )
        booking_id = booking_body["data"]["booking_id"]

        self._api("Bookings", "Xac nhan dat phong", "PUT",
                  f"/api/bookings/{booking_id}/confirm/")
        self._api("Bookings", "Check-in", "PUT",
                  f"/api/bookings/{booking_id}/check-in/")
        self._api(
            "Booking services",
            "Them dich vu vao booking",
            "POST",
            f"/api/bookings/{booking_id}/services/",
            201,
            {"service_id": self.service.id, "quantity": 2},
            "Insert BookingService voi dich vu An sang buffet",
        )
        self._api("Bookings", "Check-out", "PUT",
                  f"/api/bookings/{booking_id}/check-out/")

        invoice_body = self._api("Invoices", "Xem hoa don theo booking", "GET",
                                 f"/api/bookings/{booking_id}/invoice/")
        invoice_id = invoice_body["data"]["id"]
        self._api(
            "Invoices",
            "Thanh toan hoa don",
            "PUT",
            f"/api/invoices/{invoice_id}/pay/",
            200,
            {"payment_method": "chuyen_khoan"},
            "Update Invoice.payment_status bang API",
        )

        self.client.post("/api/auth/logout/", content_type="application/json")
        self._api("Auth", "Dang nhap quan ly", "POST", "/api/auth/login/", 200, {
            "username": self.manager.username,
            "password": "MyChi@123",
        })
        self._api("Reports", "Bao cao doanh thu", "GET", "/api/reports/revenue/")

        self._db_check(
            "Booking da tra phong",
            Booking.all_objects.filter(id=booking_id, status="da_tra_phong").exists(),
            "Booking ton tai tren DB va da tra phong",
        )
        self._db_check(
            "Room ve trang thai trong",
            Room.all_objects.filter(id=self.room.id, status="trong").exists(),
            "Room duoc mo lai sau check-out",
        )
        self._db_check(
            "BookingService da tao",
            BookingService.all_objects.filter(booking_id=booking_id).exists(),
            "Dich vu su dung duoc luu tren DB",
        )
        self._db_check(
            "Invoice da thanh toan",
            Invoice.all_objects.filter(id=invoice_id, payment_status="da_thanh_toan").exists(),
            "Hoa don da thanh toan tren DB",
        )
        self._db_check(
            "Customer da tao",
            Customer.all_objects.filter(id=customer_id).exists(),
            "Khach hang ton tai tren DB",
        )

    def _write_report(self):
        total = len(self.rows)
        passed = sum(1 for row in self.rows if row["passed"])
        failed = total - passed
        generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        rows = "\n".join(
            f"""
            <tr class="{ 'pass' if row['passed'] else 'fail' }">
              <td>{index}</td>
              <td>{html.escape(row['group'])}</td>
              <td>{html.escape(row['action'])}</td>
              <td><code>{html.escape(row['method'])}</code></td>
              <td><code>{html.escape(row['url'])}</code></td>
              <td>{html.escape(str(row['expected']))}</td>
              <td>{html.escape(str(row['actual']))}</td>
              <td>{'PASS' if row['passed'] else 'FAIL'}</td>
              <td>{html.escape(row['note'])}</td>
            </tr>
            """
            for index, row in enumerate(self.rows, start=1)
        )
        content = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Báo cáo E2E booking flow</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2933; }}
    header {{ padding: 24px 36px; background: #f7f9fc; border-bottom: 2px solid #d8dee8; }}
    main {{ padding: 24px 36px 36px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; margin: 18px 0 24px; }}
    .box {{ border: 1px solid #d8dee8; padding: 12px; }}
    .label {{ color: #637083; font-size: 13px; }}
    .value {{ font-weight: 700; font-size: 20px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border: 1px solid #d8dee8; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
    tr.pass td:nth-child(8) {{ color: #047857; font-weight: 700; }}
    tr.fail td:nth-child(8) {{ color: #b91c1c; font-weight: 700; }}
    code {{ background: #f5f7fa; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Báo cáo E2E booking flow</h1>
    <div>Thời gian sinh báo cáo: {generated_at}</div>
    <div>Prefix dữ liệu: <code>{html.escape(self.prefix)}</code></div>
  </header>
  <main>
    <section class="summary">
      <div class="box"><div class="label">Trạng thái</div><div class="value">{'PASS' if failed == 0 else 'FAIL'}</div></div>
      <div class="box"><div class="label">Tổng bước</div><div class="value">{total}</div></div>
      <div class="box"><div class="label">PASS</div><div class="value">{passed}</div></div>
      <div class="box"><div class="label">FAIL</div><div class="value">{failed}</div></div>
    </section>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Nhóm</th>
          <th>Action</th>
          <th>Method</th>
          <th>API / DB</th>
          <th>Expected</th>
          <th>Actual</th>
          <th>Kết quả</th>
          <th>Ghi chú</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
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
    parser.add_argument("--prefix", default=None)
    args = parser.parse_args()
    BookingFlowDbRunner(prefix=args.prefix).run()


if __name__ == "__main__":
    main()
