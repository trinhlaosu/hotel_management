# Web API Quan Ly Khach San - Nhom 4

**Django + MySQL | Web API Backend | OOP + MVT | Test bang Postman**

Du an thuoc **Chu de 2: Web Applications / Backend API Server / RESTful API Server**. He thong khong co frontend, cac chuc nang duoc cung cap qua API JSON.

---

## Cong Nghe

- Python
- Django
- MySQL
- Session authentication
- JSON API

---

## Cai Dat & Chay

```bash
# 1. Cai thu vien
pip install -r requirements.txt

# 2. Tao CSDL va du lieu mau bang MySQL Workbench
# Chay scripts/script_create_db_hotel_management.sql
# Sau do chay scripts/script_insert_data_hotel_management.sql

# 3. Cau hinh database trong hotel_management/settings.py

# 4. Migrate
python manage.py makemigrations
python manage.py migrate

# 5. Chay server
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000/api/
```

---

## Cau Truc Project

```text
hotel_management/
├── core/
│   ├── utils.py
│   └── validators.py
├── hotel/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── services/
│   │   ├── room_service.py
│   │   ├── booking_service.py
│   │   ├── invoice_service.py
│   │   └── report_service.py
│   └── tests/
├── hotel_management/
│   ├── settings.py
│   └── urls.py
├── scripts/
│   ├── script_create_db_hotel_management.sql
│   └── script_insert_data_hotel_management.sql
├── manage.py
└── requirements.txt
```

---

## Co So Du Lieu

Database: `hotel_management`

He thong gom 10 bang:

| STT | Bang | Mo ta |
|-----|------|-------|
| 1 | `User` | Tai khoan dang nhap |
| 2 | `Department` | Phong ban |
| 3 | `Employee` | Nhan vien |
| 4 | `Customer` | Khach hang |
| 5 | `RoomType` | Loai phong |
| 6 | `Room` | Phong |
| 7 | `Booking` | Dat phong |
| 8 | `Invoice` | Hoa don |
| 9 | `Service` | Dich vu |
| 10 | `BookingService` | Dich vu su dung theo booking |

Tien te su dung: VND.

---

## Phan Quyen

| Role | Mo ta |
|------|-------|
| `quan_ly` | Quan ly, co quyen quan tri va xem bao cao |
| `le_tan` | Le tan/nhan vien, thao tac nghiep vu khach san |
| Guest | Chua dang nhap, chi dung duoc API dang ky/dang nhap |

Tai khoan mau:

| Role | Username | Password |
|------|----------|----------|
| `quan_ly` | `ql001` | `123456` |
| `le_tan` | `lt001` | `123456` |

---

## Full API

### 1. Xac Thuc

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| POST | `/api/auth/register/` | Dang ky tai khoan moi | Guest |
| POST | `/api/auth/login/` | Dang nhap | Guest |
| POST | `/api/auth/logout/` | Dang xuat | Dang nhap |
| GET | `/api/auth/profile/` | Xem ho so ca nhan | Dang nhap |
| PUT | `/api/auth/profile/` | Cap nhat ho so ca nhan | Dang nhap |
| PUT | `/api/auth/change-password/` | Doi mat khau | Dang nhap |

### 2. User

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/users/` | Danh sach tai khoan | `quan_ly` |
| POST | `/api/users/` | Tao tai khoan | `quan_ly` |
| GET | `/api/users/<id>/` | Chi tiet tai khoan | `quan_ly` |
| PUT | `/api/users/<id>/` | Cap nhat tai khoan | `quan_ly` |
| DELETE | `/api/users/<id>/` | Vo hieu hoa tai khoan | `quan_ly` |

### 3. Department

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/departments/` | Danh sach phong ban | Dang nhap |
| POST | `/api/departments/` | Them phong ban | `quan_ly` |
| GET | `/api/departments/<id>/` | Chi tiet phong ban | Dang nhap |
| PUT | `/api/departments/<id>/` | Cap nhat phong ban | `quan_ly` |
| DELETE | `/api/departments/<id>/` | Xoa phong ban | `quan_ly` |

### 4. Employee

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/employees/` | Danh sach nhan vien | Dang nhap |
| POST | `/api/employees/` | Them nhan vien | `quan_ly` |
| GET | `/api/employees/<id>/` | Chi tiet nhan vien | Dang nhap |
| PUT | `/api/employees/<id>/` | Cap nhat nhan vien | `quan_ly` |
| DELETE | `/api/employees/<id>/` | Vo hieu hoa nhan vien | `quan_ly` |

### 5. Customer

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/customers/` | Danh sach khach hang | Dang nhap |
| GET | `/api/customers/?customer_type=vip` | Loc khach VIP | Dang nhap |
| GET | `/api/customers/?phone=0901` | Tim theo so dien thoai | Dang nhap |
| POST | `/api/customers/` | Them khach hang | Dang nhap |
| GET | `/api/customers/<id>/` | Chi tiet khach hang | Dang nhap |
| PUT | `/api/customers/<id>/` | Cap nhat khach hang | Dang nhap |
| DELETE | `/api/customers/<id>/` | Xoa khach hang | `quan_ly` |

### 6. Room Type

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/room-types/` | Danh sach loai phong | Dang nhap |
| POST | `/api/room-types/` | Them loai phong | `quan_ly` |
| GET | `/api/room-types/<id>/` | Chi tiet loai phong | Dang nhap |
| PUT | `/api/room-types/<id>/` | Cap nhat loai phong | `quan_ly` |
| DELETE | `/api/room-types/<id>/` | Xoa loai phong | `quan_ly` |

### 7. Room

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/rooms/` | Danh sach phong | Dang nhap |
| GET | `/api/rooms/?status=trong` | Loc phong theo trang thai | Dang nhap |
| POST | `/api/rooms/` | Them phong | `quan_ly` |
| GET | `/api/rooms/<id>/` | Chi tiet phong | Dang nhap |
| PUT | `/api/rooms/<id>/` | Cap nhat phong | `quan_ly` |
| DELETE | `/api/rooms/<id>/` | Xoa phong | `quan_ly` |
| PUT | `/api/rooms/<id>/status/` | Cap nhat trang thai phong | Dang nhap |

### 8. Service

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/services/` | Danh sach dich vu dang hoat dong | Dang nhap |
| POST | `/api/services/` | Them dich vu | `quan_ly` |
| GET | `/api/services/<id>/` | Chi tiet dich vu | Dang nhap |
| PUT | `/api/services/<id>/` | Cap nhat dich vu | `quan_ly` |
| DELETE | `/api/services/<id>/` | Xoa mem dich vu | `quan_ly` |

### 9. Booking

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/bookings/` | Danh sach dat phong | Dang nhap |
| GET | `/api/bookings/?status=cho_xac_nhan` | Loc dat phong theo trang thai | Dang nhap |
| POST | `/api/bookings/` | Tao dat phong | Dang nhap |
| GET | `/api/bookings/<id>/` | Chi tiet dat phong | Dang nhap |
| PUT | `/api/bookings/<id>/` | Cap nhat ghi chu dat phong | Dang nhap |
| DELETE | `/api/bookings/<id>/` | Huy dat phong | Dang nhap |
| PUT | `/api/bookings/<id>/confirm/` | Xac nhan dat phong | Dang nhap |
| PUT | `/api/bookings/<id>/cancel/` | Huy dat phong | Dang nhap |
| PUT | `/api/bookings/<id>/check-in/` | Check-in | Dang nhap |
| PUT | `/api/bookings/<id>/check-out/` | Check-out | Dang nhap |
| GET | `/api/bookings/<id>/services/` | Danh sach dich vu cua booking | Dang nhap |
| POST | `/api/bookings/<id>/services/` | Them dich vu cho booking | Dang nhap |
| GET | `/api/bookings/<id>/invoice/` | Xem hoa don theo booking | Dang nhap |

### 10. Booking Service

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| PUT | `/api/booking-services/<id>/` | Cap nhat so luong dich vu | Dang nhap |
| DELETE | `/api/booking-services/<id>/` | Xoa dich vu khoi booking | Dang nhap |

### 11. Invoice

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/invoices/` | Danh sach hoa don | Dang nhap |
| POST | `/api/invoices/` | Tao hoa don thu cong | Dang nhap |
| GET | `/api/invoices/<id>/` | Chi tiet hoa don | Dang nhap |
| PUT | `/api/invoices/<id>/pay/` | Thanh toan hoa don | Dang nhap |

### 12. Report

| Method | Endpoint | Mo ta | Quyen |
|--------|----------|-------|-------|
| GET | `/api/reports/revenue/` | Thong ke doanh thu | `quan_ly` |
| GET | `/api/reports/revenue/?tu_ngay=2026-05-01&den_ngay=2026-05-31` | Thong ke doanh thu theo ngay | `quan_ly` |
| GET | `/api/reports/room-status/` | Thong ke trang thai phong | `quan_ly` |
| GET | `/api/reports/booking-statistics/` | Thong ke dat phong | `quan_ly` |
| GET | `/api/reports/booking-statistics/?tu_ngay=2026-05-01&den_ngay=2026-05-31` | Thong ke dat phong theo ngay | `quan_ly` |
| GET | `/api/reports/top-services/` | Top dich vu duoc su dung nhieu | `quan_ly` |
| GET | `/api/reports/top-services/?top=3` | Top N dich vu | `quan_ly` |

---

## Body Mau

### Dang Ky

```json
{
  "username": "user01",
  "password": "123456",
  "email": "user01@hotel.vn"
}
```

### Dang Nhap

```json
{
  "username": "ql001",
  "password": "123456"
}
```

### Doi Mat Khau

```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

### Tao Tai Khoan

```json
{
  "username": "lt007",
  "password": "123456",
  "email": "lt007@hotel.vn",
  "role": "le_tan"
}
```

### Them Phong Ban

```json
{
  "name": "Le tan",
  "description": "Tiep nhan khach va xu ly dat phong"
}
```

### Them Nhan Vien

```json
{
  "username": "lt008",
  "password": "123456",
  "email": "lt008@hotel.vn",
  "department_id": 2,
  "full_name": "Nguyen Van A",
  "phone": "0901000008",
  "salary": 9000000,
  "hire_date": "2026-05-24",
  "shift": "sang"
}
```

### Them Khach Hang

```json
{
  "full_name": "Nguyen Van B",
  "phone": "0911000011",
  "email": "nguyenvanb@gmail.com",
  "id_card": "079206000011",
  "address": "TP. Ho Chi Minh",
  "customer_type": "regular"
}
```

### Them Loai Phong

```json
{
  "name": "Family",
  "price_per_night": 1200000,
  "capacity": 4,
  "description": "Phong cho gia dinh"
}
```

### Them Phong

```json
{
  "room_type_id": 1,
  "room_number": "105",
  "floor": 1,
  "status": "trong"
}
```

### Cap Nhat Trang Thai Phong

```json
{
  "status": "bao_tri"
}
```

### Them Dich Vu

```json
{
  "name": "An sang buffet",
  "price": 150000,
  "description": "Buffet sang",
  "is_active": true
}
```

### Tao Dat Phong

```json
{
  "customer_id": 1,
  "room_id": 1,
  "check_in": "2026-06-10",
  "check_out": "2026-06-13",
  "note": "Khach yeu cau phong yen tinh"
}
```

### Them Dich Vu Cho Booking

```json
{
  "service_id": 1,
  "quantity": 2
}
```

### Tao Hoa Don Thu Cong

```json
{
  "booking_id": 1
}
```

### Thanh Toan Hoa Don

```json
{
  "payment_method": "chuyen_khoan"
}
```

---

## Kiem Thu

```bash
python manage.py test
```

Hoac chay rieng:

```bash
python manage.py test hotel.tests.test_views
python manage.py test hotel.tests.test_services
```

---

## Ghi Chu

- API tra ve du lieu dang JSON.
- He thong su dung session de luu trang thai dang nhap.
- Cac API can quyen se tra ve `401` neu chua dang nhap va `403` neu khong du quyen.
- Mat khau trong du an demo dang luu truc tiep theo yeu cau don gian cua do an.
