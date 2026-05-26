"""Run API scenario against the real configured database.

Usage:
    python hotel_app/tests/e2e/full_api/test_e2e_api.py
    python hotel_app/tests/e2e/full_api/test_e2e_api.py --prefix demo01
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
    Booking, BookingService, Department, Employee, Invoice, Room, RoomType,
    Service, User,
)


class RealDbApiReporter:
    def __init__(self, prefix=None):
        self.client = Client(enforce_csrf_checks=False)
        self.rows = []
        self.prefix = prefix or datetime.now().strftime("real%H%M%S")
        self.run_digits = datetime.now().strftime("%H%M%S")
        self.report_path = (
            Path(__file__).resolve().parent / "bao_cao_e2e_api.html"
        )

    def run(self):
        self._ensure_manager_user()
        self._run_scenario()
        self._write_report()

        failed = [row for row in self.rows if not row["passed"]]
        if failed:
            print(f"Co {len(failed)} API bi FAIL. Xem {self.report_path}")
            raise SystemExit(1)

        print(f"Da chay API tren DB that thanh cong. Xem {self.report_path}")

    def _ensure_manager_user(self):
        User.all_objects.update_or_create(
            username="ql001",
            defaults={
                "password": make_password("MyChi@123"),
                "email": "mychi@hotel.vn",
                "role": "quan_ly",
                "is_active": True,
                "is_deleted": False,
            },
        )

    def _api(self, group, action, method, url, expected=200, data=None, note=""):
        try:
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
            elif method == "PATCH":
                response = self.client.patch(
                    url,
                    data=json.dumps(data or {}),
                    content_type="application/json",
                )
            elif method == "DELETE":
                response = self.client.delete(url, content_type="application/json")
            else:
                raise ValueError(f"Unsupported method: {method}")
        except Exception as exc:
            response = None
            actual = "EXCEPTION"
            passed = False
            body = {}
            note = note or str(exc)
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

    def _data_id(self, body):
        data = body.get("data") if isinstance(body, dict) else {}
        if isinstance(data, dict):
            return data.get("id") or data.get("booking_id")
        return None

    def _unique_phone(self, index):
        digits = self.run_digits[-6:]
        tail = f"{digits.rjust(6, '0')}{index:02d}"
        return f"09{tail}"[:15]

    def _unique_id_card(self, index):
        digits = self.run_digits[-6:].rjust(6, "0")
        return f"079206{digits}{index:02d}"[:20]

    def _run_scenario(self):
        prefix = self.prefix

        self._api("Auth", "Dang ky tai khoan", "POST", "/api/auth/register/", 201, {
            "username": f"lt_register_{prefix}",
            "password": "123456",
            "email": f"lt_register_{prefix}@hotel.vn",
        }, "Register user le_tan moi, mac dinh chua active")

        self._api("Auth", "Dang nhap quan ly", "POST", "/api/auth/login/", 200, {
            "username": "ql001",
            "password": "MyChi@123",
        })
        self._api("Auth", "Xem ho so", "GET", "/api/auth/profile/")
        self._api("Auth", "Cap nhat ho so", "PUT", "/api/auth/profile/", 200, {
            "email": "mychi@hotel.vn",
        }, "Update profile theo user mau ql001")
        self._api("Auth", "Doi mat khau tam", "PUT", "/api/auth/change-password/", 200, {
            "old_password": "MyChi@123",
            "new_password": "MyChi@123Temp",
        }, "Kiem tra change-password")
        self._api("Auth", "Doi lai mat khau mau", "PUT", "/api/auth/change-password/", 200, {
            "old_password": "MyChi@123Temp",
            "new_password": "MyChi@123",
        }, "Khoi phuc mat khau ql001 ve data mau")

        user_id = self._data_id(self._api(
            "Users", "Them tai khoan", "POST", "/api/users/", 201, {
                "username": f"lt_e2e_{prefix}",
                "password": "123456",
                "email": f"lt_e2e_{prefix}@hotel.vn",
                "role": "le_tan",
            }, "Insert User theo nhom le_tan giong data mau",
        ))
        self._api("Users", "Danh sach tai khoan", "GET", "/api/users/")
        self._api("Users", "Chi tiet tai khoan", "GET", f"/api/users/{user_id}/")
        self._api("Users", "Cap nhat tai khoan", "PUT", f"/api/users/{user_id}/", 200, {
            "email": f"lt_e2e_{prefix}_updated@hotel.vn",
            "role": "le_tan",
            "is_active": True,
        }, "Update User van giu role le_tan theo data mau")
        self._api("Users", "Patch tai khoan", "PATCH", f"/api/users/{user_id}/", 200, {
            "email": f"lt_e2e_{prefix}_patch@hotel.vn",
        }, "PATCH User.email")
        self._api("Users", "Vo hieu tai khoan", "POST", f"/api/users/{user_id}/disable/")
        self._api("Users", "Kich hoat tai khoan", "POST", f"/api/users/{user_id}/enable/")

        dept_id = self._data_id(self._api(
            "Departments", "Them phong ban", "POST", "/api/departments/", 201, {
                "name": f"Le tan E2E {prefix}",
                "description": "Phong ban le tan duoc tao theo data mau",
            }, "Insert Department map voi phong ban Le tan",
        ))
        self._api("Departments", "Danh sach phong ban", "GET", "/api/departments/")
        self._api("Departments", "Chi tiet phong ban", "GET", f"/api/departments/{dept_id}/")
        self._api("Departments", "Cap nhat phong ban", "PUT", f"/api/departments/{dept_id}/", 200, {
            "name": f"Le tan E2E {prefix} update",
            "description": "Cap nhat phong ban theo nhom Le tan",
        }, "Update Department map voi phong ban Le tan")
        self._api("Departments", "Patch phong ban", "PATCH", f"/api/departments/{dept_id}/", 200, {
            "description": "PATCH phong ban Le tan E2E",
        }, "PATCH Department.description")

        emp_id = self._data_id(self._api(
            "Employees", "Them nhan vien", "POST", "/api/employees/", 201, {
                "username": f"lt_e2e_emp_{prefix}",
                "password": "123456",
                "email": f"lt_e2e_emp_{prefix}@hotel.vn",
                "department_id": dept_id,
                "full_name": f"Vo Mong Chuyen E2E {prefix}",
                "phone": self._unique_phone(1),
                "hire_date": "2026-01-01",
                "salary": 8500000,
                "shift": "sang",
            }, "Insert Employee theo mau le tan",
        ))
        self._api("Employees", "Danh sach nhan vien", "GET", "/api/employees/")
        self._api("Employees", "Chi tiet nhan vien", "GET", f"/api/employees/{emp_id}/")
        self._api("Employees", "Cap nhat nhan vien", "PUT", f"/api/employees/{emp_id}/", 200, {
            "department_id": dept_id,
            "full_name": f"Vo Mong Chuyen E2E {prefix} update",
            "phone": self._unique_phone(3),
            "salary": 9000000,
            "shift": "chieu",
            "status": "dang_lam",
        }, "Update Employee van map nhom le tan")
        self._api("Employees", "Patch nhan vien", "PATCH", f"/api/employees/{emp_id}/", 200, {
            "shift": "toi",
        }, "PATCH Employee.shift")

        customer_id = self._data_id(self._api(
            "Customers", "Them khach hang", "POST", "/api/customers/", 201, {
                "full_name": f"Nguyen Tat Hung E2E {prefix}",
                "phone": self._unique_phone(2),
                "email": f"nguyentathung.e2e.{prefix}@gmail.com",
                "id_card": self._unique_id_card(1),
                "address": "TP. Ho Chi Minh",
                "customer_type": "regular",
            }, "Insert Customer theo mau Nguyen Tat Hung",
        ))
        self._api("Customers", "Danh sach khach hang", "GET", "/api/customers/")
        self._api("Customers", "Chi tiet khach hang", "GET", f"/api/customers/{customer_id}/")
        self._api("Customers", "Cap nhat khach hang", "PUT", f"/api/customers/{customer_id}/", 200, {
            "full_name": f"Nguyen Tat Hung E2E {prefix} update",
            "phone": self._unique_phone(4),
            "email": f"nguyentathung.e2e.{prefix}.update@gmail.com",
            "address": "Quan Phu Nhuan, TP. Ho Chi Minh",
            "customer_type": "regular",
        }, "Update Customer van theo nhom regular")
        self._api("Customers", "Patch khach hang", "PATCH", f"/api/customers/{customer_id}/", 200, {
            "customer_type": "vip",
        }, "PATCH Customer.customer_type")

        room_type_id = self._data_id(self._api(
            "Room types", "Them loai phong", "POST", "/api/room-types/", 201, {
                "name": f"Suite E2E {prefix}",
                "price_per_night": 1500000,
                "capacity": 3,
                "description": "Loai phong Suite map theo data mau",
            }, "Insert RoomType theo mau Suite",
        ))
        self._api("Room types", "Danh sach loai phong", "GET", "/api/room-types/")
        self._api("Room types", "Chi tiet loai phong", "GET", f"/api/room-types/{room_type_id}/")
        self._api("Room types", "Cap nhat loai phong", "PUT", f"/api/room-types/{room_type_id}/", 200, {
            "name": f"Suite E2E {prefix} update",
            "price_per_night": 1500000,
            "capacity": 3,
            "description": "Cap nhat nhung van giu thong so Suite mau",
        }, "Update RoomType theo mau Suite")
        self._api("Room types", "Patch loai phong", "PATCH", f"/api/room-types/{room_type_id}/", 200, {
            "capacity": 4,
        }, "PATCH RoomType.capacity")

        room_id = self._data_id(self._api(
            "Rooms", "Them phong", "POST", "/api/rooms/", 201, {
                "room_type_id": room_type_id,
                "room_number": f"4E{self.run_digits[-4:]}",
                "floor": 4,
                "status": "trong",
            }, "Insert Room map tang 4 nhom Suite",
        ))
        self._api("Rooms", "Danh sach phong", "GET", "/api/rooms/")
        self._api("Rooms", "Chi tiet phong", "GET", f"/api/rooms/{room_id}/")
        self._api("Rooms", "Cap nhat phong", "PUT", f"/api/rooms/{room_id}/", 200, {
            "room_type_id": room_type_id,
            "floor": 4,
            "status": "trong",
        }, "Update Room van map tang 4")
        self._api("Rooms", "Patch phong", "PATCH", f"/api/rooms/{room_id}/", 200, {
            "floor": 5,
        }, "PATCH Room.floor")
        self._api("Rooms", "Doi trang thai phong", "PUT", f"/api/rooms/{room_id}/status/", 200, {
            "status": "bao_tri",
        }, "Update Room.status trong DB that")
        self._api("Rooms", "Mo lai phong trong", "PUT", f"/api/rooms/{room_id}/status/", 200, {
            "status": "trong",
        })

        service_id = self._data_id(self._api(
            "Services", "Them dich vu", "POST", "/api/services/", 201, {
                "name": f"Spa & Massage E2E {prefix}",
                "price": 350000,
                "description": "Dich vu Spa & Massage map theo data mau",
            }, "Insert Service theo mau Spa & Massage",
        ))
        self._api("Services", "Danh sach dich vu", "GET", "/api/services/")
        self._api("Services", "Chi tiet dich vu", "GET", f"/api/services/{service_id}/")
        self._api("Services", "Cap nhat dich vu", "PUT", f"/api/services/{service_id}/", 200, {
            "name": f"Spa & Massage E2E {prefix} update",
            "price": 350000,
            "description": "Cap nhat nhung van giu gia dich vu mau",
            "is_active": True,
        }, "Update Service theo mau Spa & Massage")
        self._api("Services", "Patch dich vu", "PATCH", f"/api/services/{service_id}/", 200, {
            "description": "PATCH dich vu Spa & Massage E2E",
        }, "PATCH Service.description")

        booking_id = self._data_id(self._api(
            "Bookings", "Tao dat phong", "POST", "/api/bookings/", 201, {
                "customer_id": customer_id,
                "room_id": room_id,
                "check_in": "2028-12-01",
                "check_out": "2028-12-04",
                "note": f"Booking tao tren DB that {prefix}",
            }, "Insert Booking va Invoice vao DB that",
        ))
        self._api("Bookings", "Danh sach dat phong", "GET", "/api/bookings/")
        self._api("Bookings", "Chi tiet dat phong", "GET", f"/api/bookings/{booking_id}/")
        self._api("Bookings", "Cap nhat ghi chu dat phong", "PUT", f"/api/bookings/{booking_id}/", 200, {
            "note": f"Booking tao tren DB that {prefix} update",
        }, "Update Booking.note trong DB that")
        cancel_booking_id = self._data_id(self._api(
            "Bookings", "Tao booking de huy", "POST", "/api/bookings/", 201, {
                "customer_id": customer_id,
                "room_id": room_id,
                "check_in": "2030-01-10",
                "check_out": "2030-01-12",
                "note": f"Booking cancel E2E {prefix}",
            }, "Tao booking rieng de test cancel",
        ))
        self._api("Bookings", "Huy dat phong", "PUT", f"/api/bookings/{cancel_booking_id}/cancel/")
        self._api("Bookings", "Xac nhan dat phong", "PUT", f"/api/bookings/{booking_id}/confirm/")
        self._api("Bookings", "Check-in", "PUT", f"/api/bookings/{booking_id}/check-in/")

        booking_service_id = self._data_id(self._api(
            "Booking services", "Them dich vu vao booking", "POST",
            f"/api/bookings/{booking_id}/services/", 201, {
                "service_id": service_id,
                "quantity": 2,
            }, "Insert BookingService va cap nhat Invoice tren DB that",
        ))
        self._api(
            "Booking services",
            "Danh sach dich vu theo booking",
            "GET",
            f"/api/bookings/{booking_id}/services/",
        )
        self._api(
            "Booking services",
            "Cap nhat so luong dich vu",
            "PUT",
            f"/api/booking-services/{booking_service_id}/",
            200,
            {"quantity": 3},
            "Update BookingService va Invoice tren DB that",
        )

        self._api("Bookings", "Check-out", "PUT", f"/api/bookings/{booking_id}/check-out/")
        invoice_id = self._data_id(self._api(
            "Bookings", "Xem hoa don theo booking", "GET",
            f"/api/bookings/{booking_id}/invoice/",
        ))
        self._api("Invoices", "Danh sach hoa don", "GET", "/api/invoices/")
        self._api("Invoices", "Chi tiet hoa don", "GET", f"/api/invoices/{invoice_id}/")
        manual_booking = Booking.all_objects.create(
            customer_id=customer_id,
            room_id=room_id,
            check_in="2030-02-01",
            check_out="2030-02-03",
            status="da_xac_nhan",
            note=f"Booking manual invoice E2E {prefix}",
        )
        manual_invoice_id = self._data_id(self._api(
            "Invoices", "Lap hoa don thu cong", "POST", "/api/invoices/", 201, {
                "booking_id": manual_booking.id,
            }, "POST /api/invoices/ cho booking chua co invoice",
        ))
        self._api("Invoices", "Patch hoa don", "PATCH", f"/api/invoices/{manual_invoice_id}/", 200, {
            "payment_method": "tien_mat",
        }, "PATCH Invoice.payment_method")
        self._api("Invoices", "Thanh toan hoa don", "PUT", f"/api/invoices/{invoice_id}/pay/", 200, {
            "payment_method": "chuyen_khoan",
        }, "Update Invoice.payment_status trong DB that")

        self._api("Reports", "Bao cao doanh thu", "GET", "/api/reports/revenue/")
        self._api("Reports", "Bao cao trang thai phong", "GET", "/api/reports/room-status/")
        self._api("Reports", "Bao cao dat phong", "GET", "/api/reports/booking-statistics/")
        self._api("Reports", "Top dich vu", "GET", "/api/reports/top-services/?top=3")

        self._api("Booking services", "Xoa dich vu khoi booking", "DELETE", f"/api/booking-services/{booking_service_id}/")
        self._api("Invoices", "Xoa mem hoa don thu cong", "DELETE", f"/api/invoices/{manual_invoice_id}/")
        self._api("Bookings", "Xoa booking da huy", "DELETE", f"/api/bookings/{cancel_booking_id}/")
        self._api("Services", "Xoa/vo hieu dich vu", "DELETE", f"/api/services/{service_id}/")
        self._api("Rooms", "Xoa mem phong", "DELETE", f"/api/rooms/{room_id}/")
        self._api("Room types", "Xoa mem loai phong", "DELETE", f"/api/room-types/{room_type_id}/")
        self._api("Customers", "Xoa mem khach hang", "DELETE", f"/api/customers/{customer_id}/")
        self._api("Employees", "Vo hieu nhan vien", "DELETE", f"/api/employees/{emp_id}/")
        self._api("Departments", "Xoa mem phong ban", "DELETE", f"/api/departments/{dept_id}/")
        self._api("Users", "Vo hieu tai khoan", "DELETE", f"/api/users/{user_id}/")
        self._api("Auth", "Dang xuat", "POST", "/api/auth/logout/")
        self._api("Auth", "Chan khi chua dang nhap", "GET", "/api/users/", 401)

        self._add_db_check("DB", "User da duoc tao", User.all_objects.filter(id=user_id).exists())
        self._add_db_check("DB", "Department da soft delete", Department.all_objects.filter(id=dept_id, is_deleted=True).exists())
        self._add_db_check("DB", "Employee da nghi viec", Employee.all_objects.filter(id=emp_id, status="nghi_viec").exists())
        self._add_db_check("DB", "RoomType da soft delete", RoomType.all_objects.filter(id=room_type_id, is_deleted=True).exists())
        self._add_db_check("DB", "Room da soft delete", Room.all_objects.filter(id=room_id, is_deleted=True).exists())
        self._add_db_check("DB", "Service da vo hieu", Service.all_objects.filter(id=service_id, is_active=False).exists())
        self._add_db_check("DB", "Booking da tra phong", Booking.all_objects.filter(id=booking_id, status="da_tra_phong").exists())
        self._add_db_check("DB", "Booking da huy", Booking.all_objects.filter(id=cancel_booking_id, status="da_huy").exists())
        self._add_db_check("DB", "BookingService da xoa", not BookingService.all_objects.filter(id=booking_service_id).exists())
        self._add_db_check("DB", "Invoice da thanh toan", Invoice.all_objects.filter(id=invoice_id, payment_status="da_thanh_toan").exists())
        self._add_db_check("DB", "Invoice thu cong da soft delete", Invoice.all_objects.filter(id=manual_invoice_id, is_deleted=True).exists())

    def _add_db_check(self, group, action, ok):
        self.rows.append({
            "group": group,
            "action": action,
            "method": "CHECK",
            "url": "hotel_management",
            "expected": True,
            "actual": ok,
            "passed": ok is True,
            "note": "Kiem tra truc tiep DB that sau khi goi API",
        })

    def _write_report(self):
        total = len(self.rows)
        passed = sum(1 for row in self.rows if row["passed"])
        failed = total - passed
        generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        row_html = "\n".join(
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
  <title>Kết quả chạy API trên DB thật - Nhóm 04</title>
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
    <h1>Kết quả chạy API trên DB thật - Nhóm 04</h1>
    <div>Thời gian sinh báo cáo: {generated_at}</div>
    <div>Database: <code>{settings.DATABASES['default']['NAME']}</code></div>
    <div>Prefix dữ liệu sinh ra: <code>{html.escape(self.prefix)}</code></div>
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
      <tbody>{row_html}</tbody>
    </table>
  </main>
</body>
</html>
"""
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Chay full API tren database that va sinh bao cao HTML."
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Tien to du lieu sinh ra de de tim trong DB, vi du demo01.",
    )
    args = parser.parse_args()
    RealDbApiReporter(prefix=args.prefix).run()


if __name__ == "__main__":
    main()
