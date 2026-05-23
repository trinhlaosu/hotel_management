# Web API Quản lý Khách sạn – Nhóm 4
**Django + MySQL | OOP + MVT | 28 chức năng**

---

## Cài đặt & Chạy

```bash
# 1. Cài thư viện
pip install -r requirements.txt

# 2. Chạy SQL tạo CSDL
# Mở MySQL Workbench → chạy hotel_db.sql

# 3. Cấu hình PASSWORD trong mysite/settings.py

# 4. Migrate
python manage.py makemigrations
python manage.py migrate

# 5. Chạy server
python manage.py runserver
```

---

## Cấu trúc Project

```
mysite/
├── hotel/              ← App chính
│   ├── models.py       ← 10 bảng CSDL
│   ├── views.py        ← 28 chức năng (CBV)
│   ├── urls.py         ← REST endpoints
│   └── services/       ← Business logic (OOP)
│       ├── room_service.py
│       ├── booking_service.py
│       ├── invoice_service.py
│       └── report_service.py
├── core/               ← Tiện ích dùng chung
│   ├── utils.py        ← Auth session, phan_hoi()
│   └── validators.py   ← Kiểm tra dữ liệu
├── mysite/             ← Project settings
└── manage.py
```

---

## Danh sách API (test bằng Postman)

### Xác thực
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | /api/auth/login/ | Đăng nhập |
| POST | /api/auth/logout/ | Đăng xuất |
| GET  | /api/auth/profile/ | Xem hồ sơ |
| PUT  | /api/auth/profile/ | Cập nhật hồ sơ |
| PUT  | /api/auth/change-password/ | Đổi mật khẩu |

### Đặt phòng (quan trọng nhất)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET  | /api/rooms/?status=trong | Tìm phòng trống |
| POST | /api/bookings/ | Tạo đặt phòng |
| PUT  | /api/bookings/1/confirm/ | Xác nhận |
| PUT  | /api/bookings/1/check-in/ | Check-in |
| POST | /api/bookings/1/services/ | Thêm dịch vụ |
| PUT  | /api/bookings/1/check-out/ | Check-out |
| PUT  | /api/invoices/1/pay/ | Thanh toán |

### Thống kê (Quản lý)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | /api/reports/revenue/ | Doanh thu |
| GET | /api/reports/room-status/ | Tình trạng phòng |
| GET | /api/reports/booking-statistics/ | Thống kê booking |
| GET | /api/reports/top-services/ | Dịch vụ phổ biến |

---

## Body mẫu – Đăng nhập
```json
{ "username": "admin", "password": "123456" }
```

## Body mẫu – Tạo đặt phòng
```json
{
  "customer_id": 1,
  "room_id": 1,
  "check_in": "2026-06-10",
  "check_out": "2026-06-13",
  "note": "Kỷ niệm ngày cưới"
}
```

## Body mẫu – Thanh toán
```json
{ "payment_method": "chuyen_khoan" }
```

---

## Phân quyền
| Role | Mô tả |
|------|-------|
| quan_ly | Quản lý – toàn quyền |
| le_tan  | Lễ tân – thao tác phòng, booking, hóa đơn |
