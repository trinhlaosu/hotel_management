import json
from datetime import date

from django.test import Client, TestCase

from hotel_app.models import (
    Customer, Department, Employee, Room, RoomType, Service, User,
)


class BaseTest(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

        self.quan_ly = User.objects.create(
            username="admin_mychi",
            password="123456",
            email="mychi@hotel.com",
            role="quan_ly",
        )
        self.le_tan = User.objects.create(
            username="nv_chuyen",
            password="123456",
            email="chuyen@hotel.com",
            role="le_tan",
        )

        self.dept = Department.objects.create(name="Le tan")
        self.emp = Employee.objects.create(
            user=self.le_tan,
            department=self.dept,
            full_name="Vo Mong Chuyen",
            phone="0901111111",
            salary=8_000_000,
            hire_date=date(2024, 1, 1),
        )

        self.customer = Customer.objects.create(
            full_name="Nguyen Van A",
            phone="0909090901",
            id_card="012345678901",
        )

        self.room_type = RoomType.objects.create(
            name="Standard",
            price_per_night=500_000,
            capacity=2,
        )
        self.room = Room.objects.create(
            room_type=self.room_type,
            room_number="101",
            floor=1,
            status="trong",
        )

        self.service = Service.objects.create(
            name="An sang",
            price=150_000,
            is_active=True,
        )

    def login(self, username="admin_mychi", password="123456"):
        return self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": username, "password": password}),
            content_type="application/json",
        )

    def post(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

    def put(self, url, data=None):
        return self.client.put(
            url,
            data=json.dumps(data or {}),
            content_type="application/json",
        )

    def delete(self, url):
        return self.client.delete(url, content_type="application/json")

    def _tao_booking(self, check_in="2026-07-01", check_out="2026-07-04"):
        res = self.post("/api/bookings/", {
            "customer_id": self.customer.id,
            "room_id": self.room.id,
            "check_in": check_in,
            "check_out": check_out,
        })
        return res.json()["data"]["booking_id"]
