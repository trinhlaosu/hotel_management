"""Run API scenario against the real configured database.

Ngoai viec kiem tra HTTP status code, file nay con xac minh:
  - Data tra ve co dung gia tri khong (field value assertion).
  - Tinh toan hoa don chinh xac (room_charge, service_charge, total).
  - Cac chuyen doi trang thai dung quy trinh.
  - List endpoint tra ve list; detail tra ve dung id.

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

# Gia tri data mau dung lam gia tri nen khi check
_ROOM_TYPE_PRICE = 1_500_000   # price_per_night Suite E2E
_SVC_PRICE       = 350_000     # price dich vu Spa & Massage E2E
_BOOKING_NIGHTS  = 3           # 2028-12-01 → 2028-12-04
_SVC_QTY_1       = 2           # so luong dich vu lan 1
_SVC_QTY_2       = 3           # so luong dich vu sau khi cap nhat
_SVC_SUB_1       = _SVC_PRICE * _SVC_QTY_1   # 700_000
_SVC_SUB_2       = _SVC_PRICE * _SVC_QTY_2   # 1_050_000


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
            print(f"Co {len(failed)} buoc FAIL. Xem {self.report_path}")
            raise SystemExit(1)

        print(f"Da chay API tren DB that thanh cong. Xem {self.report_path}")

    # ── Seed ──────────────────────────────────────────────────────────────────

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

    # ── Data / check helpers ──────────────────────────────────────────────────

    def _g(self, body, *path):
        """Safe-get: navigate nested dict by path, return None if missing."""
        cur = body
        for key in path:
            if isinstance(cur, dict):
                cur = cur.get(key)
            else:
                return None
        return cur

    def _num(self, body, *path):
        """Get numeric value from body path. Returns None if not found/parseable."""
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

    def _add_db_check(self, group, action, ok):
        self.rows.append({
            "group": group, "action": action,
            "method": "CHECK", "url": "hotel_management DB",
            "expected": True, "actual": ok,
            "passed": ok is True,
            "note": "Kiem tra truc tiep DB that sau khi goi API",
        })

    # ── Scenario ──────────────────────────────────────────────────────────────

    def _run_scenario(self):
        prefix = self.prefix

        # ── AUTH ──────────────────────────────────────────────────────────────
        self._api("Auth", "Dang ky tai khoan moi", "POST", "/api/auth/register/", 201, {
            "username": f"lt_register_{prefix}",
            "password": "123456",
            "email": f"lt_register_{prefix}@hotel.vn",
        }, "Register user le_tan moi, mac dinh chua active")

        self._api("Auth", "Dang nhap quan ly", "POST", "/api/auth/login/", 200, {
            "username": "ql001", "password": "MyChi@123",
        })

        profile = self._api("Auth", "Xem ho so ca nhan", "GET", "/api/auth/profile/")
        self._check("Auth", "Profile.username == ql001",
                    self._g(profile, "data", "username") == "ql001")
        self._check("Auth", "Profile.role == quan_ly",
                    self._g(profile, "data", "role") == "quan_ly")

        self._api("Auth", "Cap nhat ho so ca nhan", "PUT", "/api/auth/profile/", 200, {
            "email": "mychi@hotel.vn",
        })
        self._api("Auth", "Doi mat khau tam", "PUT", "/api/auth/change-password/", 200, {
            "old_password": "MyChi@123", "new_password": "MyChi@123Temp",
        })
        self._api("Auth", "Khoi phuc mat khau ve mau", "PUT", "/api/auth/change-password/", 200, {
            "old_password": "MyChi@123Temp", "new_password": "MyChi@123",
        })

        # ── USERS ─────────────────────────────────────────────────────────────
        u_body = self._api("Users", "Them tai khoan le tan", "POST", "/api/users/", 201, {
            "username": f"lt_e2e_{prefix}",
            "password": "123456",
            "email": f"lt_e2e_{prefix}@hotel.vn",
            "role": "le_tan",
        })
        user_id = self._data_id(u_body)
        self._check("Users", "User.id duoc tra ve", user_id is not None)
        self._check("Users", "User.username khop",
                    self._g(u_body, "data", "username") == f"lt_e2e_{prefix}")
        self._check("Users", "User.role = le_tan",
                    self._g(u_body, "data", "role") == "le_tan")

        ul = self._api("Users", "Danh sach tai khoan", "GET", "/api/users/")
        self._check("Users", "List users tra ve list",
                    isinstance(self._g(ul, "data"), list))

        uf_let = self._api("Users", "Loc theo role le_tan", "GET", "/api/users/?role=le_tan")
        self._check("Users", "Filter role=le_tan: moi item co role=le_tan",
                    all(isinstance(i, dict) and i.get("role") == "le_tan"
                        for i in (self._g(uf_let, "data") or [])))

        self._api("Users", "Loc theo role quan_ly", "GET", "/api/users/?role=quan_ly")
        self._api("Users", "Loc theo is_active=true", "GET", "/api/users/?is_active=true")
        self._api("Users", "Tim kiem theo username", "GET",
                  f"/api/users/?search=lt_e2e_{prefix}")
        self._api("Users", "Sap xep theo username", "GET", "/api/users/?ordering=username")

        ud = self._api("Users", "Chi tiet tai khoan", "GET", f"/api/users/{user_id}/")
        self._check("Users", "User detail tra ve dung id",
                    self._g(ud, "data", "id") == user_id)

        upd_email = f"lt_e2e_{prefix}_updated@hotel.vn"
        uput = self._api("Users", "Cap nhat tai khoan (PUT)", "PUT",
                         f"/api/users/{user_id}/", 200, {
                             "email": upd_email, "role": "le_tan", "is_active": True,
                         })
        self._check("Users", "User.email sau PUT khop",
                    self._g(uput, "data", "email") == upd_email)

        patch_email = f"lt_e2e_{prefix}_patch@hotel.vn"
        upatch = self._api("Users", "Cap nhat email (PATCH)", "PATCH",
                           f"/api/users/{user_id}/", 200, {
                               "email": patch_email,
                           })
        self._check("Users", "User.email sau PATCH khop",
                    self._g(upatch, "data", "email") == patch_email)

        self._api("Users", "Vo hieu tai khoan", "POST", f"/api/users/{user_id}/disable/")
        self._api("Users", "Kich hoat tai khoan", "POST", f"/api/users/{user_id}/enable/")

        # ── DEPARTMENTS ───────────────────────────────────────────────────────
        d_body = self._api("Departments", "Them phong ban", "POST", "/api/departments/", 201, {
            "name": f"Le tan E2E {prefix}",
            "description": "Phong ban le tan duoc tao theo data mau",
        })
        dept_id = self._data_id(d_body)
        self._check("Departments", "Dept.id duoc tra ve", dept_id is not None)
        self._check("Departments", "Dept.name khop",
                    self._g(d_body, "data", "name") == f"Le tan E2E {prefix}")

        dl = self._api("Departments", "Danh sach phong ban", "GET", "/api/departments/")
        self._check("Departments", "List departments tra ve list",
                    isinstance(self._g(dl, "data"), list))

        self._api("Departments", "Tim kiem phong ban", "GET",
                  "/api/departments/?search=Le+tan+E2E")
        self._api("Departments", "Sap xep theo ten", "GET", "/api/departments/?ordering=name")

        dd = self._api("Departments", "Chi tiet phong ban", "GET",
                       f"/api/departments/{dept_id}/")
        self._check("Departments", "Dept detail tra ve dung id",
                    self._g(dd, "data", "id") == dept_id)

        dput_name = f"Le tan E2E {prefix} update"
        dput = self._api("Departments", "Cap nhat phong ban (PUT)", "PUT",
                         f"/api/departments/{dept_id}/", 200, {
                             "name": dput_name,
                             "description": "Cap nhat phong ban le tan",
                         })
        self._check("Departments", "Dept.name sau PUT khop",
                    self._g(dput, "data", "name") == dput_name)

        dpatch_desc = "PATCH phong ban Le tan E2E"
        dpatch = self._api("Departments", "Cap nhat mo ta (PATCH)", "PATCH",
                           f"/api/departments/{dept_id}/", 200, {
                               "description": dpatch_desc,
                           })
        self._check("Departments", "Dept.description sau PATCH khop",
                    self._g(dpatch, "data", "description") == dpatch_desc)

        # ── EMPLOYEES ─────────────────────────────────────────────────────────
        e_body = self._api("Employees", "Them nhan vien", "POST", "/api/employees/", 201, {
            "username": f"lt_e2e_emp_{prefix}",
            "password": "123456",
            "email": f"lt_e2e_emp_{prefix}@hotel.vn",
            "department_id": dept_id,
            "full_name": f"Vo Mong Chuyen E2E {prefix}",
            "phone": self._unique_phone(1),
            "hire_date": "2026-01-01",
            "salary": 8500000,
            "shift": "sang",
        })
        emp_id = self._data_id(e_body)
        self._check("Employees", "Employee.id duoc tra ve", emp_id is not None)
        self._check("Employees", "Employee.shift = sang sau create",
                    self._g(e_body, "data", "shift") == "sang")
        self._check("Employees", "Employee.salary = 8.500.000 sau create",
                    self._num(e_body, "data", "salary") == 8_500_000)

        el = self._api("Employees", "Danh sach nhan vien", "GET", "/api/employees/")
        self._check("Employees", "List employees tra ve list",
                    isinstance(self._g(el, "data"), list))

        ef_sang = self._api("Employees", "Loc theo shift sang", "GET", "/api/employees/?shift=sang")
        self._check("Employees", "Filter shift=sang: moi item co shift=sang",
                    all(isinstance(i, dict) and i.get("shift") == "sang"
                        for i in (self._g(ef_sang, "data") or [])))

        ef_dlam = self._api("Employees", "Loc theo status dang_lam", "GET",
                            "/api/employees/?status=dang_lam")
        self._check("Employees", "Filter status=dang_lam: moi item co status=dang_lam",
                    all(isinstance(i, dict) and i.get("status") == "dang_lam"
                        for i in (self._g(ef_dlam, "data") or [])))
        self._api("Employees", "Tim kiem nhan vien", "GET",
                  "/api/employees/?search=Vo+Mong+Chuyen")
        self._api("Employees", "Sap xep theo ten nhan vien", "GET",
                  "/api/employees/?ordering=full_name")

        ed = self._api("Employees", "Chi tiet nhan vien", "GET", f"/api/employees/{emp_id}/")
        self._check("Employees", "Employee detail tra ve dung id",
                    self._g(ed, "data", "id") == emp_id)

        eput = self._api("Employees", "Cap nhat nhan vien (PUT)", "PUT",
                         f"/api/employees/{emp_id}/", 200, {
                             "department_id": dept_id,
                             "full_name": f"Vo Mong Chuyen E2E {prefix} update",
                             "phone": self._unique_phone(3),
                             "salary": 9000000,
                             "shift": "chieu",
                             "status": "dang_lam",
                         })
        self._check("Employees", "Employee.shift = chieu sau PUT",
                    self._g(eput, "data", "shift") == "chieu")
        self._check("Employees", "Employee.salary = 9.000.000 sau PUT",
                    self._num(eput, "data", "salary") == 9_000_000)

        epatch = self._api("Employees", "Cap nhat ca lam (PATCH)", "PATCH",
                           f"/api/employees/{emp_id}/", 200, {"shift": "toi"})
        self._check("Employees", "Employee.shift = toi sau PATCH",
                    self._g(epatch, "data", "shift") == "toi")

        # ── CUSTOMERS ─────────────────────────────────────────────────────────
        c_body = self._api("Customers", "Them khach hang", "POST", "/api/customers/", 201, {
            "full_name": f"Nguyen Tat Hung E2E {prefix}",
            "phone": self._unique_phone(2),
            "email": f"nguyentathung.e2e.{prefix}@gmail.com",
            "id_card": self._unique_id_card(1),
            "address": "TP. Ho Chi Minh",
            "customer_type": "regular",
        })
        customer_id = self._data_id(c_body)
        self._check("Customers", "Customer.id duoc tra ve", customer_id is not None)
        self._check("Customers", "Customer.customer_type = regular sau create",
                    self._g(c_body, "data", "customer_type") == "regular")

        cl = self._api("Customers", "Danh sach khach hang", "GET", "/api/customers/")
        self._check("Customers", "List customers tra ve list",
                    isinstance(self._g(cl, "data"), list))

        cf_reg = self._api("Customers", "Loc theo loai regular", "GET",
                           "/api/customers/?customer_type=regular")
        self._check("Customers", "Filter regular: moi item co customer_type=regular",
                    all(isinstance(i, dict) and i.get("customer_type") == "regular"
                        for i in (self._g(cf_reg, "data") or [])))

        cf_vip = self._api("Customers", "Loc theo loai vip", "GET",
                           "/api/customers/?customer_type=vip")
        self._check("Customers", "Filter vip: moi item co customer_type=vip",
                    all(isinstance(i, dict) and i.get("customer_type") == "vip"
                        for i in (self._g(cf_vip, "data") or [])))
        self._api("Customers", "Tim kiem khach hang", "GET",
                  "/api/customers/?search=Nguyen+Tat+Hung")
        self._api("Customers", "Sap xep theo ten khach hang", "GET",
                  "/api/customers/?ordering=full_name")

        cd = self._api("Customers", "Chi tiet khach hang", "GET",
                       f"/api/customers/{customer_id}/")
        self._check("Customers", "Customer detail tra ve dung id",
                    self._g(cd, "data", "id") == customer_id)

        cpatch = self._api("Customers", "Cap nhat loai khach (PATCH)", "PATCH",
                           f"/api/customers/{customer_id}/", 200,
                           {"customer_type": "vip"})
        self._check("Customers", "Customer.customer_type = vip sau PATCH",
                    self._g(cpatch, "data", "customer_type") == "vip")

        cput_phone = self._unique_phone(4)
        cput = self._api("Customers", "Cap nhat khach hang (PUT)", "PUT",
                         f"/api/customers/{customer_id}/", 200, {
                             "full_name": f"Nguyen Tat Hung E2E {prefix} update",
                             "phone": cput_phone,
                             "email": f"nguyentathung.e2e.{prefix}.update@gmail.com",
                             "address": "Quan Phu Nhuan, TP. Ho Chi Minh",
                             "customer_type": "vip",
                         })
        self._check("Customers", "Customer.phone sau PUT khop",
                    self._g(cput, "data", "phone") == cput_phone)

        # ── ROOM TYPES ────────────────────────────────────────────────────────
        rt_body = self._api("Room types", "Them loai phong", "POST", "/api/room-types/", 201, {
            "name": f"Suite E2E {prefix}",
            "price_per_night": _ROOM_TYPE_PRICE,
            "capacity": 3,
            "description": "Loai phong Suite map theo data mau",
        })
        room_type_id = self._data_id(rt_body)
        self._check("Room types", "RoomType.id duoc tra ve", room_type_id is not None)
        self._check("Room types", f"RoomType.price_per_night = {_ROOM_TYPE_PRICE:,}",
                    self._num(rt_body, "data", "price_per_night") == _ROOM_TYPE_PRICE)
        self._check("Room types", "RoomType.capacity = 3 sau create",
                    self._g(rt_body, "data", "capacity") == 3)

        rtl = self._api("Room types", "Danh sach loai phong", "GET", "/api/room-types/")
        self._check("Room types", "List room-types tra ve list",
                    isinstance(self._g(rtl, "data"), list))

        self._api("Room types", "Tim kiem loai phong", "GET",
                  "/api/room-types/?search=Suite+E2E")
        self._api("Room types", "Sap xep theo gia phong", "GET",
                  "/api/room-types/?ordering=price_per_night")
        self._api("Room types", "Sap xep theo suc chua giam dan", "GET",
                  "/api/room-types/?ordering=-capacity")

        rtd = self._api("Room types", "Chi tiet loai phong", "GET",
                        f"/api/room-types/{room_type_id}/")
        self._check("Room types", "RoomType detail tra ve dung id",
                    self._g(rtd, "data", "id") == room_type_id)

        rtput_name = f"Suite E2E {prefix} update"
        rtput = self._api("Room types", "Cap nhat loai phong (PUT)", "PUT",
                          f"/api/room-types/{room_type_id}/", 200, {
                              "name": rtput_name,
                              "price_per_night": _ROOM_TYPE_PRICE,
                              "capacity": 3,
                              "description": "Cap nhat nhung van giu thong so Suite mau",
                          })
        self._check("Room types", "RoomType.name sau PUT khop",
                    self._g(rtput, "data", "name") == rtput_name)

        rtpatch = self._api("Room types", "Cap nhat suc chua (PATCH)", "PATCH",
                            f"/api/room-types/{room_type_id}/", 200, {"capacity": 4})
        self._check("Room types", "RoomType.capacity = 4 sau PATCH",
                    self._g(rtpatch, "data", "capacity") == 4)

        # ── ROOMS ─────────────────────────────────────────────────────────────
        room_number = f"4E{self.run_digits[-4:]}"
        r_body = self._api("Rooms", "Them phong moi", "POST", "/api/rooms/", 201, {
            "room_type_id": room_type_id,
            "room_number": room_number,
            "floor": 4,
            "status": "trong",
        })
        room_id = self._data_id(r_body)
        self._check("Rooms", "Room.id duoc tra ve", room_id is not None)
        self._check("Rooms", "Room.status = trong sau create",
                    self._g(r_body, "data", "status") == "trong")
        self._check("Rooms", "Room.floor = 4 sau create",
                    self._g(r_body, "data", "floor") == 4)

        rl = self._api("Rooms", "Danh sach phong", "GET", "/api/rooms/")
        self._check("Rooms", "List rooms tra ve list",
                    isinstance(self._g(rl, "data"), list))

        self._api("Rooms", "Loc theo tang 4", "GET", "/api/rooms/?floor=4")
        rf_trong = self._api("Rooms", "Loc theo trang thai trong", "GET", "/api/rooms/?status=trong")
        self._check("Rooms", "Filter status=trong: moi item co status=trong",
                    all(isinstance(i, dict) and i.get("status") == "trong"
                        for i in (self._g(rf_trong, "data") or [])))
        self._api("Rooms", "Loc theo room_type_id", "GET",
                  f"/api/rooms/?room_type_id={room_type_id}")
        self._api("Rooms", "Loc theo suc chua toi thieu 4", "GET", "/api/rooms/?capacity=4")
        self._api("Rooms", "Tim kiem theo so phong", "GET",
                  f"/api/rooms/?search={room_number}")
        self._api("Rooms", "Sap xep theo tang", "GET", "/api/rooms/?ordering=floor")

        rd = self._api("Rooms", "Chi tiet phong", "GET", f"/api/rooms/{room_id}/")
        self._check("Rooms", "Room detail tra ve dung id",
                    self._g(rd, "data", "id") == room_id)
        self._check("Rooms", "Room.status = trong (detail)",
                    self._g(rd, "data", "status") == "trong")

        self._api("Rooms", "Cap nhat phong (PUT)", "PUT", f"/api/rooms/{room_id}/", 200, {
            "room_type_id": room_type_id, "floor": 4, "status": "trong",
        })

        rpatch = self._api("Rooms", "Cap nhat tang (PATCH)", "PATCH",
                           f"/api/rooms/{room_id}/", 200, {"floor": 5})
        self._check("Rooms", "Room.floor = 5 sau PATCH",
                    self._g(rpatch, "data", "floor") == 5)

        rs_bao_tri = self._api("Rooms", "Doi trang thai sang bao tri", "PUT",
                               f"/api/rooms/{room_id}/status/", 200, {"status": "bao_tri"})
        self._check("Rooms", "Room.status = bao_tri sau doi",
                    self._g(rs_bao_tri, "data", "status") == "bao_tri")

        rs_trong = self._api("Rooms", "Mo lai phong (trong)", "PUT",
                             f"/api/rooms/{room_id}/status/", 200, {"status": "trong"})
        self._check("Rooms", "Room.status = trong sau mo lai",
                    self._g(rs_trong, "data", "status") == "trong")

        # ── SERVICES ──────────────────────────────────────────────────────────
        sv_body = self._api("Services", "Them dich vu", "POST", "/api/services/", 201, {
            "name": f"Spa & Massage E2E {prefix}",
            "price": _SVC_PRICE,
            "description": "Dich vu Spa & Massage map theo data mau",
        })
        service_id = self._data_id(sv_body)
        self._check("Services", "Service.id duoc tra ve", service_id is not None)
        self._check("Services", f"Service.price = {_SVC_PRICE:,} sau create",
                    self._num(sv_body, "data", "price") == _SVC_PRICE)

        svl = self._api("Services", "Danh sach dich vu (active)", "GET", "/api/services/")
        self._check("Services", "List services tra ve list",
                    isinstance(self._g(svl, "data"), list))

        self._api("Services", "Loc is_active=true", "GET", "/api/services/?is_active=true")
        self._api("Services", "Tim kiem dich vu Spa", "GET", "/api/services/?search=Spa")
        self._api("Services", "Sap xep theo gia giam dan", "GET", "/api/services/?ordering=-price")
        self._api("Services", "Sap xep theo ten dich vu", "GET", "/api/services/?ordering=name")

        svd = self._api("Services", "Chi tiet dich vu", "GET", f"/api/services/{service_id}/")
        self._check("Services", "Service detail tra ve dung id",
                    self._g(svd, "data", "id") == service_id)

        svput = self._api("Services", "Cap nhat dich vu (PUT)", "PUT",
                          f"/api/services/{service_id}/", 200, {
                              "name": f"Spa & Massage E2E {prefix} update",
                              "price": _SVC_PRICE,
                              "description": "Cap nhat nhung van giu gia dich vu mau",
                              "is_active": True,
                          })
        self._check("Services", "Service.is_active = True sau PUT",
                    self._g(svput, "data", "is_active") is True)

        svpatch_desc = "PATCH dich vu Spa & Massage E2E"
        svpatch = self._api("Services", "Cap nhat mo ta dich vu (PATCH)", "PATCH",
                            f"/api/services/{service_id}/", 200,
                            {"description": svpatch_desc})
        self._check("Services", "Service.description sau PATCH khop",
                    self._g(svpatch, "data", "description") == svpatch_desc)

        # ── PRICING ───────────────────────────────────────────────────────────
        pr_vip = self._api(
            "Pricing", "Tinh gia booking (VIP, 3 dem)", "POST",
            "/api/pricing/calculate-booking-price/", 200, {
                "room_id": room_id,
                "check_in": "2028-08-10",
                "check_out": "2028-08-13",
                "customer_type": "vip",
            },
        )
        self._check("Pricing", "Pricing.so_dem = 3 (VIP)",
                    self._num(pr_vip, "data", "so_dem") == 3,
                    "2028-08-10 → 2028-08-13 = 3 dem")
        self._check("Pricing", "Pricing.final_price > 0 (VIP)",
                    (self._num(pr_vip, "data", "final_price") or 0) > 0)

        pr_reg = self._api(
            "Pricing", "Tinh gia booking (regular, 4 dem)", "POST",
            "/api/pricing/calculate-booking-price/", 200, {
                "room_id": room_id,
                "check_in": "2029-01-01",
                "check_out": "2029-01-05",
                "customer_type": "regular",
            },
        )
        self._check("Pricing", "Pricing.so_dem = 4 (regular)",
                    self._num(pr_reg, "data", "so_dem") == 4,
                    "2029-01-01 → 2029-01-05 = 4 dem")
        self._check("Pricing", "Pricing.final_price > 0 (regular)",
                    (self._num(pr_reg, "data", "final_price") or 0) > 0)

        # ── BOOKINGS ──────────────────────────────────────────────────────────
        b_body = self._api(
            "Bookings", "Tao dat phong chinh", "POST", "/api/bookings/", 201, {
                "customer_id": customer_id,
                "room_id": room_id,
                "check_in": "2028-12-01",
                "check_out": "2028-12-04",
                "note": f"Booking chinh tren DB that {prefix}",
            },
        )
        booking_id = self._data_id(b_body)
        self._check("Bookings", "booking_id duoc tra ve", booking_id is not None)
        self._check("Bookings", f"Booking.tong_tien > 0 ({_BOOKING_NIGHTS} dem)",
                    (self._num(b_body, "data", "tong_tien") or 0) > 0)

        # Lay invoice_id ngay sau khi tao booking (invoice duoc tao cung luc)
        inv_init = self._api(
            "Invoices", "Xem hoa don ngay sau khi tao booking", "GET",
            f"/api/bookings/{booking_id}/invoice/",
            note="Invoice duoc tao tu dong khi tao booking",
        )
        invoice_id = self._data_id(inv_init)
        self._check("Invoices", "invoice_id duoc tra ve ngay sau booking",
                    invoice_id is not None)
        self._check("Invoices", "room_charge > 0 ngay sau tao booking",
                    (self._num(inv_init, "data", "room_charge") or 0) > 0,
                    f"Phong Suite {_ROOM_TYPE_PRICE:,}/dem x {_BOOKING_NIGHTS} dem")
        self._check("Invoices", "service_charge = 0 khi chua co dich vu",
                    self._num(inv_init, "data", "service_charge") == 0)
        room_charge = self._num(inv_init, "data", "room_charge") or 0

        bl = self._api("Bookings", "Danh sach dat phong", "GET", "/api/bookings/")
        self._check("Bookings", "List bookings tra ve list",
                    isinstance(self._g(bl, "data"), list))

        self._api("Bookings", "Loc theo customer_id", "GET",
                  f"/api/bookings/?customer_id={customer_id}")
        self._api("Bookings", "Loc theo room_id", "GET",
                  f"/api/bookings/?room_id={room_id}")
        self._api("Bookings", "Loc theo trang thai cho_xac_nhan", "GET",
                  "/api/bookings/?status=cho_xac_nhan")
        self._api("Bookings", "Loc theo khoang ngay check_in", "GET",
                  "/api/bookings/?tu_ngay=2028-12-01&den_ngay=2028-12-31")
        self._api("Bookings", "Sap xep theo check_in", "GET",
                  "/api/bookings/?ordering=check_in")
        self._api("Bookings", "Sap xep theo created_at giam dan", "GET",
                  "/api/bookings/?ordering=-created_at")

        bd = self._api("Bookings", "Chi tiet dat phong", "GET",
                       f"/api/bookings/{booking_id}/")
        self._check("Bookings", f"Booking.so_dem = {_BOOKING_NIGHTS}",
                    self._num(bd, "data", "so_dem") == _BOOKING_NIGHTS,
                    "2028-12-01 → 2028-12-04 = 3 dem")
        self._check("Bookings", "Booking.tien_phong > 0",
                    (self._num(bd, "data", "tien_phong") or 0) > 0)

        self._api("Bookings", "Cap nhat ghi chu (PUT)", "PUT",
                  f"/api/bookings/{booking_id}/", 200,
                  {"note": f"Booking update ghi chu {prefix}"})

        cancel_body = self._api(
            "Bookings", "Tao booking de huy", "POST", "/api/bookings/", 201, {
                "customer_id": customer_id,
                "room_id": room_id,
                "check_in": "2030-01-10",
                "check_out": "2030-01-12",
                "note": f"Booking cancel E2E {prefix}",
            }, "Tao booking rieng de test cancel va delete",
        )
        cancel_booking_id = self._data_id(cancel_body)

        self._api("Bookings", "Huy dat phong (action cancel)", "PUT",
                  f"/api/bookings/{cancel_booking_id}/cancel/")
        self._api("Bookings", "Xac nhan dat phong chinh", "PUT",
                  f"/api/bookings/{booking_id}/confirm/")
        self._api("Bookings", "Check-in dat phong chinh", "PUT",
                  f"/api/bookings/{booking_id}/check-in/")

        # ── BOOKING SERVICES ──────────────────────────────────────────────────
        bs_body = self._api(
            "Booking services", "Them dich vu vao booking (qty=2)", "POST",
            f"/api/bookings/{booking_id}/services/", 201, {
                "service_id": service_id, "quantity": _SVC_QTY_1,
            },
        )
        booking_service_id = self._data_id(bs_body)
        self._check("Booking services", "BookingService.id duoc tra ve",
                    booking_service_id is not None)
        self._check("Booking services",
                    f"BookingService.quantity = {_SVC_QTY_1} sau create",
                    self._g(bs_body, "data", "quantity") == _SVC_QTY_1)
        self._check("Booking services",
                    f"BookingService.subtotal = {_SVC_SUB_1:,} ({_SVC_QTY_1} x {_SVC_PRICE:,})",
                    self._num(bs_body, "data", "subtotal") == _SVC_SUB_1)

        bsl = self._api("Booking services", "Danh sach dich vu theo booking", "GET",
                        f"/api/bookings/{booking_id}/services/")
        self._check("Booking services", "List booking-services tra ve list",
                    isinstance(self._g(bsl, "data"), list))

        # Kiem tra hoa don sau khi them dich vu qty=2
        inv_after_add = self._api(
            "Invoices", f"Kiem tra invoice sau them dich vu (qty={_SVC_QTY_1})", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices",
                    f"service_charge = {_SVC_SUB_1:,} sau qty={_SVC_QTY_1}",
                    self._num(inv_after_add, "data", "service_charge") == _SVC_SUB_1,
                    f"{_SVC_QTY_1} x {_SVC_PRICE:,} = {_SVC_SUB_1:,}")
        self._check("Invoices",
                    f"total = room_charge + {_SVC_SUB_1:,} sau qty={_SVC_QTY_1}",
                    self._num(inv_after_add, "data", "total") == room_charge + _SVC_SUB_1)

        # Cap nhat so luong dich vu qty=2 → qty=3
        self._api(
            "Booking services", f"Cap nhat so luong dich vu (qty={_SVC_QTY_2})", "PUT",
            f"/api/booking-services/{booking_service_id}/", 200,
            {"quantity": _SVC_QTY_2},
        )

        # Kiem tra hoa don sau khi cap nhat qty=3
        inv_after_upd = self._api(
            "Invoices", f"Kiem tra invoice sau cap nhat dich vu (qty={_SVC_QTY_2})", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices",
                    f"service_charge = {_SVC_SUB_2:,} sau qty={_SVC_QTY_2}",
                    self._num(inv_after_upd, "data", "service_charge") == _SVC_SUB_2,
                    f"{_SVC_QTY_2} x {_SVC_PRICE:,} = {_SVC_SUB_2:,}")
        self._check("Invoices",
                    f"total = room_charge + {_SVC_SUB_2:,} sau qty={_SVC_QTY_2}",
                    self._num(inv_after_upd, "data", "total") == room_charge + _SVC_SUB_2)

        # ── CHECK-OUT ─────────────────────────────────────────────────────────
        self._api("Bookings", "Check-out dat phong chinh", "PUT",
                  f"/api/bookings/{booking_id}/check-out/")

        # ── INVOICES (sau check-out) ───────────────────────────────────────────
        # GET invoice qua booking (endpoint nay bo payment_method va paid_at)
        self._api("Invoices", "Xem hoa don cuoi qua booking (sau check-out)", "GET",
                  f"/api/bookings/{booking_id}/invoice/")

        inv_pre_pay = self._api(
            "Invoices", "Xem hoa don cuoi (full detail, chua thanh toan)", "GET",
            f"/api/invoices/{invoice_id}/",
        )
        self._check("Invoices", "Invoice.payment_status = chua_thanh_toan truoc khi tra tien",
                    self._g(inv_pre_pay, "data", "payment_status") == "chua_thanh_toan")
        self._check("Invoices", "Invoice.paid_at = null truoc khi tra tien",
                    self._g(inv_pre_pay, "data", "paid_at") is None)
        self._check("Invoices", "Invoice.total > 0 (sau check-out)",
                    (self._num(inv_pre_pay, "data", "total") or 0) > 0)

        il = self._api("Invoices", "Danh sach hoa don", "GET", "/api/invoices/")
        self._check("Invoices", "List invoices tra ve list",
                    isinstance(self._g(il, "data"), list))

        if_chtt = self._api("Invoices", "Loc chua thanh toan", "GET",
                            "/api/invoices/?payment_status=chua_thanh_toan")
        self._check("Invoices", "Filter chua_thanh_toan: moi item chua thanh toan",
                    all(isinstance(i, dict) and i.get("payment_status") == "chua_thanh_toan"
                        for i in (self._g(if_chtt, "data") or [])))
        self._api("Invoices", "Sap xep theo tong tien giam dan", "GET",
                  "/api/invoices/?ordering=-total")
        self._api("Invoices", "Sap xep theo ngay tao", "GET",
                  "/api/invoices/?ordering=-created_at")

        ivd = self._api("Invoices", "Chi tiet hoa don", "GET",
                        f"/api/invoices/{invoice_id}/")
        self._check("Invoices", "Invoice detail tra ve dung id",
                    self._g(ivd, "data", "id") == invoice_id)

        # Tao manual booking qua ORM de test POST /api/invoices/
        manual_booking = Booking.all_objects.create(
            customer_id=customer_id,
            room_id=room_id,
            check_in="2030-02-01",
            check_out="2030-02-03",
            status="da_xac_nhan",
            note=f"Booking manual invoice E2E {prefix}",
        )
        mi_body = self._api(
            "Invoices", "Lap hoa don thu cong", "POST", "/api/invoices/", 201, {
                "booking_id": manual_booking.id,
            }, "POST /api/invoices/ cho booking chua co invoice",
        )
        manual_invoice_id = self._data_id(mi_body)
        self._check("Invoices", "Manual invoice id duoc tra ve",
                    manual_invoice_id is not None)

        mipatch = self._api(
            "Invoices", "Cap nhat payment_method (PATCH)", "PATCH",
            f"/api/invoices/{manual_invoice_id}/", 200,
            {"payment_method": "tien_mat"},
        )
        self._check("Invoices", "Invoice.payment_method = tien_mat sau PATCH",
                    self._g(mipatch, "data", "payment_method") == "tien_mat")

        self._api("Invoices", "Loc theo payment_method tien_mat", "GET",
                  "/api/invoices/?payment_method=tien_mat")

        # Thanh toan hoa don chinh
        pay_body = self._api(
            "Invoices", "Thanh toan hoa don chinh (chuyen_khoan)", "PUT",
            f"/api/invoices/{invoice_id}/pay/", 200,
            {"payment_method": "chuyen_khoan"},
        )
        self._check("Invoices", "Invoice.payment_status = da_thanh_toan sau thanh toan",
                    self._g(pay_body, "data", "payment_status") == "da_thanh_toan")
        self._check("Invoices", "Invoice.payment_method = chuyen_khoan sau thanh toan",
                    self._g(pay_body, "data", "payment_method") == "chuyen_khoan")
        self._check("Invoices", "Invoice.paid_at khong null sau thanh toan",
                    self._g(pay_body, "data", "paid_at") is not None)
        self._check("Invoices", "Invoice.total khong doi sau thanh toan",
                    self._num(pay_body, "data", "total") == room_charge + _SVC_SUB_2)

        if_paid = self._api("Invoices", "Loc hoa don da thanh toan", "GET",
                            "/api/invoices/?payment_status=da_thanh_toan")
        self._check("Invoices", "Filter da_thanh_toan: moi item da thanh toan",
                    all(isinstance(i, dict) and i.get("payment_status") == "da_thanh_toan"
                        for i in (self._g(if_paid, "data") or [])))
        self._api("Invoices", "Loc theo payment_method chuyen_khoan", "GET",
                  "/api/invoices/?payment_method=chuyen_khoan")

        # ── REPORTS ───────────────────────────────────────────────────────────
        rv = self._api("Reports", "Bao cao doanh thu (tat ca)", "GET",
                       "/api/reports/revenue/")
        self._check("Reports", "Revenue: co field so_hoa_don_da_tt va tong_doanh_thu",
                    self._g(rv, "data", "so_hoa_don_da_tt") is not None and
                    self._g(rv, "data", "tong_doanh_thu") is not None)
        self._check("Reports", "Revenue: so_hoa_don_da_tt >= 1 (co invoice vua thanh toan)",
                    (self._num(rv, "data", "so_hoa_don_da_tt") or 0) >= 1)
        self._check("Reports", "Revenue: tong_doanh_thu > 0",
                    (self._num(rv, "data", "tong_doanh_thu") or 0) > 0)

        self._api("Reports", "Bao cao doanh thu (loc ngay)", "GET",
                  "/api/reports/revenue/?tu_ngay=2028-01-01&den_ngay=2028-12-31")

        rs = self._api("Reports", "Bao cao trang thai phong", "GET",
                       "/api/reports/room-status/")
        self._check("Reports", "Room-status: co du 4 field (tong, trong, co_khach, bao_tri)",
                    all(self._g(rs, "data", k) is not None
                        for k in ["tong", "trong", "co_khach", "bao_tri"]))
        self._check("Reports", "Room-status: tong = trong + co_khach + bao_tri",
                    self._num(rs, "data", "tong") == (
                        (self._num(rs, "data", "trong") or 0) +
                        (self._num(rs, "data", "co_khach") or 0) +
                        (self._num(rs, "data", "bao_tri") or 0)))

        bks = self._api("Reports", "Bao cao dat phong (tat ca)", "GET",
                        "/api/reports/booking-statistics/")
        self._check("Reports", "Booking-stats: co field tong va da_tra_phong",
                    self._g(bks, "data", "tong") is not None and
                    self._g(bks, "data", "da_tra_phong") is not None)
        self._check("Reports", "Booking-stats: da_tra_phong >= 1 (booking chinh da checkout)",
                    (self._num(bks, "data", "da_tra_phong") or 0) >= 1)
        self._check("Reports", "Booking-stats: da_huy >= 1 (cancel_booking)",
                    (self._num(bks, "data", "da_huy") or 0) >= 1)
        self._api("Reports", "Bao cao dat phong (loc ngay)", "GET",
                  "/api/reports/booking-statistics/?tu_ngay=2028-12-01&den_ngay=2028-12-31")

        top3 = self._api("Reports", "Top 3 dich vu su dung nhieu nhat", "GET",
                         "/api/reports/top-services/?top=3")
        self._check("Reports", "Top-services tra ve list",
                    isinstance(self._g(top3, "data"), list))
        self._check("Reports", "Top-services tra ve toi da 3 phan tu",
                    len(self._g(top3, "data") or []) <= 3)
        self._check("Reports", "Top-services: moi item co field ten_dich_vu, tong_so_luong, tong_tien",
                    all(all(k in (i or {}) for k in ["ten_dich_vu", "tong_so_luong", "tong_tien"])
                        for i in (self._g(top3, "data") or [])))

        self._api("Reports", "Top 5 dich vu su dung nhieu nhat", "GET",
                  "/api/reports/top-services/?top=5")

        # ── KIEM TRA PERMISSION (le_tan khong duoc truy cap manager-only) ───────
        self._api("Auth", "[Perm] Tam dang xuat manager", "POST", "/api/auth/logout/")
        self._api("Auth", "[Perm] Le tan dang nhap", "POST", "/api/auth/login/", 200, {
            "username": f"lt_e2e_{prefix}", "password": "123456",
        })

        # Cac endpoint chi danh cho manager → le_tan phai nhan 403
        self._api("Permission", "Le tan tao user → 403", "POST", "/api/users/", 403, {
            "username": "blocked_user", "password": "123456",
            "email": "blocked@test.vn", "role": "le_tan",
        })
        self._api("Permission", "Le tan tao phong ban → 403", "POST",
                  "/api/departments/", 403, {"name": "Blocked Dept"})
        self._api("Permission", "Le tan tao loai phong → 403", "POST",
                  "/api/room-types/", 403,
                  {"name": "Blocked RT", "price_per_night": 100000, "capacity": 1})
        self._api("Permission", "Le tan tao phong → 403", "POST",
                  "/api/rooms/", 403,
                  {"room_type_id": 1, "room_number": "BLOCKED", "floor": 1})
        self._api("Permission", "Le tan tao dich vu → 403", "POST",
                  "/api/services/", 403,
                  {"name": "Blocked Service", "price": 100000})
        self._api("Permission", "Le tan xem bao cao doanh thu → 403", "GET",
                  "/api/reports/revenue/", 403)
        self._api("Permission", "Le tan xem bao cao dat phong → 403", "GET",
                  "/api/reports/booking-statistics/", 403)
        self._api("Permission", "Le tan xem bao cao trang thai phong → 403", "GET",
                  "/api/reports/room-status/", 403)
        self._api("Permission", "Le tan xem top dich vu → 403", "GET",
                  "/api/reports/top-services/", 403)

        # Cac endpoint le_tan DUOC phep → phai nhan 200
        self._api("Permission", "Le tan xem danh sach phong → 200", "GET", "/api/rooms/")
        self._api("Permission", "Le tan xem danh sach khach hang → 200", "GET",
                  "/api/customers/")
        self._api("Permission", "Le tan xem danh sach booking → 200", "GET", "/api/bookings/")
        self._api("Permission", "Le tan xem danh sach dich vu → 200", "GET", "/api/services/")
        self._api("Permission", "Le tan xem danh sach phong ban → 200", "GET",
                  "/api/departments/")

        self._api("Auth", "[Perm] Le tan dang xuat", "POST", "/api/auth/logout/")
        self._api("Auth", "[Perm] Manager dang nhap lai", "POST", "/api/auth/login/", 200, {
            "username": "ql001", "password": "MyChi@123",
        })

        # ── CLEANUP ───────────────────────────────────────────────────────────
        self._api("Booking services", "Xoa dich vu khoi booking", "DELETE",
                  f"/api/booking-services/{booking_service_id}/")
        self._api("Invoices", "Xoa mem hoa don thu cong", "DELETE",
                  f"/api/invoices/{manual_invoice_id}/")
        self._api("Bookings", "Xoa/huy booking da huy", "DELETE",
                  f"/api/bookings/{cancel_booking_id}/")
        self._api("Services", "Vo hieu dich vu (DELETE)", "DELETE",
                  f"/api/services/{service_id}/")
        self._api("Rooms", "Xoa mem phong", "DELETE", f"/api/rooms/{room_id}/")
        self._api("Room types", "Xoa mem loai phong", "DELETE",
                  f"/api/room-types/{room_type_id}/")
        self._api("Customers", "Xoa mem khach hang", "DELETE",
                  f"/api/customers/{customer_id}/")
        self._api("Employees", "Vo hieu nhan vien (DELETE)", "DELETE",
                  f"/api/employees/{emp_id}/")
        self._api("Departments", "Xoa mem phong ban", "DELETE",
                  f"/api/departments/{dept_id}/")
        self._api("Users", "Vo hieu tai khoan le tan (DELETE)", "DELETE",
                  f"/api/users/{user_id}/")

        # ── AUTH LOGOUT & UNAUTHENTICATED CHECKS ──────────────────────────────
        self._api("Auth", "Dang xuat", "POST", "/api/auth/logout/")
        self._api("Auth", "Chan khi chua dang nhap: users", "GET", "/api/users/", 401)
        self._api("Auth", "Chan khi chua dang nhap: bookings", "GET", "/api/bookings/", 401)
        self._api("Auth", "Chan khi chua dang nhap: rooms", "GET", "/api/rooms/", 401)
        self._api("Auth", "Chan khi chua dang nhap: reports", "GET",
                  "/api/reports/revenue/", 401)
        self._api("Auth", "Chan khi chua dang nhap: invoices", "GET", "/api/invoices/", 401)

        # ── DB VERIFICATION ───────────────────────────────────────────────────
        self._add_db_check("DB", "User le tan da duoc tao",
                           User.all_objects.filter(id=user_id).exists())
        self._add_db_check("DB", "Department da soft delete",
                           Department.all_objects.filter(id=dept_id, is_deleted=True).exists())
        self._add_db_check("DB", "Employee da nghi viec",
                           Employee.all_objects.filter(id=emp_id, status="nghi_viec").exists())
        self._add_db_check("DB", "RoomType da soft delete",
                           RoomType.all_objects.filter(id=room_type_id, is_deleted=True).exists())
        self._add_db_check("DB", "Room da soft delete",
                           Room.all_objects.filter(id=room_id, is_deleted=True).exists())
        self._add_db_check("DB", "Service da bi vo hieu (is_active=False)",
                           Service.all_objects.filter(id=service_id, is_active=False).exists())
        self._add_db_check("DB", "Booking chinh da tra phong",
                           Booking.all_objects.filter(
                               id=booking_id, status="da_tra_phong").exists())
        self._add_db_check("DB", "Booking cancel da huy",
                           Booking.all_objects.filter(
                               id=cancel_booking_id, status="da_huy").exists())
        self._add_db_check("DB", "BookingService da xoa (hard delete)",
                           not BookingService.all_objects.filter(
                               id=booking_service_id).exists())
        self._add_db_check("DB", "Invoice chinh da thanh toan",
                           Invoice.all_objects.filter(
                               id=invoice_id, payment_status="da_thanh_toan").exists())
        self._add_db_check("DB", "Invoice.payment_method = chuyen_khoan",
                           Invoice.all_objects.filter(
                               id=invoice_id, payment_method="chuyen_khoan").exists())
        self._add_db_check("DB", "Invoice.paid_at duoc set",
                           Invoice.all_objects.filter(
                               id=invoice_id, paid_at__isnull=False).exists())
        self._add_db_check("DB", "Invoice thu cong da soft delete",
                           Invoice.all_objects.filter(
                               id=manual_invoice_id, is_deleted=True).exists())

    # ── Report ────────────────────────────────────────────────────────────────

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

        row_html = "\n".join(
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
  <title>Báo cáo Kiểm thử E2E – Toàn bộ API – Nhóm 04</title>
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
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 32px; }}
    th, td {{ border: 1px solid #d8dee8; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
    tr.pass td:nth-child(8) {{ color: #047857; font-weight: 700; }}
    tr.fail td:nth-child(8) {{ color: #b91c1c; font-weight: 700; }}
    tr.check-row {{ background: #fafafa; }}
    tr.check-row td:nth-child(4) code {{ background: #e0f2fe; color: #0369a1; }}
    code {{ background: #f5f7fa; padding: 1px 4px; border-radius: 4px; font-size: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>Báo cáo Kiểm thử E2E – Toàn bộ API – Nhóm 04</h1>
    <div>Thời gian sinh báo cáo: {generated_at}</div>
    <div>Database: <code>{settings.DATABASES['default']['NAME']}</code></div>
    <div>Prefix dữ liệu sinh ra: <code>{html.escape(self.prefix)}</code></div>
    <div style="margin-top:8px;font-size:13px;color:#637083">
      Hàng <code style="background:#e0f2fe;color:#0369a1">CHECK</code>
      là bước xác minh nội dung response / DB, không phải HTTP call.
    </div>
  </header>
  <main>
    <section class="summary">
      <div class="box">
        <div class="label">Trạng thái</div>
        <div class="value {'ok' if failed == 0 else 'ng'}">{'PASS' if failed == 0 else 'FAIL'}</div>
      </div>
      <div class="box"><div class="label">Tổng bước</div><div class="value">{total}</div></div>
      <div class="box"><div class="label">PASS</div><div class="value ok">{passed}</div></div>
      <div class="box"><div class="label">FAIL</div><div class="value ng">{failed}</div></div>
    </section>

    <h2>Tổng hợp theo nhóm API</h2>
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
        "--prefix", default=None,
        help="Tien to du lieu sinh ra de de tim trong DB, vi du demo01.",
    )
    args = parser.parse_args()
    RealDbApiReporter(prefix=args.prefix).run()


if __name__ == "__main__":
    main()
