# Xây Dựng RESTful API Quản Lý Khách Sạn

**Nhóm 04 - Python Django + MySQL**

Dự án này được thực hiện theo yêu cầu đồ án môn học: xây dựng ứng dụng **Web API / Backend API Server / RESTful API Server**, không cần giao diện frontend. Hệ thống tập trung vào nghiệp vụ quản lý khách sạn: tài khoản, nhân viên, khách hàng, phòng, đặt phòng, dịch vụ, hóa đơn và thống kê.

---

## 1. Đáp Ứng Yêu Cầu Đồ Án

| Yêu cầu của thầy | Phần đáp ứng trong dự án |
|---|---|
| Sử dụng ngôn ngữ Python | Dự án viết bằng Python |
| Xây dựng Web API / Backend API Server | Sử dụng Django để tạo API JSON |
| Không bắt buộc frontend | Dự án không xây dựng frontend, test bằng Postman |
| Có cơ sở dữ liệu | Sử dụng MySQL, database `hotel_management` |
| Số bảng CSDL từ 5 đến 10 | Có đúng 10 bảng chính |
| Có tối thiểu 2 đối tượng người dùng | Có `quan_ly` và `le_tan` |
| Có API đăng nhập, đăng ký | Có `/api/auth/login/`, `/api/auth/register/`; tài khoản đăng ký cần quản lý duyệt |
| Có REST API GET, POST, PUT, DELETE | Có đủ các method GET, POST, PUT, DELETE |
| Có API thể hiện chức năng quan trọng | Có API đặt phòng, check-in, check-out, thanh toán, thống kê |
| Kiểm thử API bằng Postman | Có file Postman collection theo luồng 12 API chính |
| Áp dụng OOP / MVC hoặc MVT | Dùng Django MVT, models và service classes |
| Có báo cáo, slide, source code, video demo | README này hỗ trợ chạy source và demo API |

---

## 2. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python |
| Framework | Django |
| Database | MySQL |
| Kiến trúc | Django MVT |
| API response | JSON |
| Kiểm thử API | Postman |
| Unit test | Django TestCase |

Dự án dùng Django cơ bản theo phong cách trên lớp:

- `django.views.View`
- `JsonResponse`
- `@csrf_exempt`
- Tự đọc JSON request body
- Không dùng Django REST Framework
- Mật khẩu người dùng được mã hóa bằng Django password hasher

Mật khẩu không được lưu trực tiếp trong database. Khi tạo tài khoản, đăng ký hoặc đổi mật khẩu, hệ thống dùng `make_password()` của Django để hash mật khẩu theo dạng `pbkdf2_sha256`. Khi đăng nhập, hệ thống dùng `check_password()` để so sánh mật khẩu người dùng nhập với chuỗi hash đã lưu. Chuỗi hash có dạng:

```text
algorithm$iterations$salt$hash
```

---

## 3. Cấu Trúc Thư Mục

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
│   ├── migrations/
│   └── tests/
├── hotel_management/
│   ├── settings.py
│   └── urls.py
├── scripts/
│   ├── script_create_db_hotel_management.sql
│   └── script_insert_data_hotel_management.sql
├── postman/
│   └── hotel_management_postman_collection.json
├── manage.py
├── requirements.txt
└── README.md
```

---

## 4. Cơ Sở Dữ Liệu

Database: `hotel_management`

Hệ thống gồm đúng **10 bảng**:

| STT | Bảng | Mô tả |
|---|---|---|
| 1 | `User` | Tài khoản đăng nhập, phân quyền |
| 2 | `Department` | Phòng ban trong khách sạn |
| 3 | `Employee` | Hồ sơ nhân viên |
| 4 | `Customer` | Thông tin khách hàng |
| 5 | `RoomType` | Loại phòng và giá phòng |
| 6 | `Room` | Phòng khách sạn |
| 7 | `Booking` | Thông tin đặt phòng |
| 8 | `Invoice` | Hóa đơn thanh toán |
| 9 | `Service` | Dịch vụ khách sạn |
| 10 | `BookingService` | Dịch vụ sử dụng theo từng booking |

Quan hệ chính:

```text
User 1 - 1 Employee
Department 1 - n Employee
RoomType 1 - n Room
Customer 1 - n Booking
Room 1 - n Booking
Employee 1 - n Booking
Booking 1 - 1 Invoice
Booking 1 - n BookingService
Service 1 - n BookingService
```

Tiền tệ sử dụng trong hệ thống: **VND**.

---

## 5. Đối Tượng Người Dùng Và Phân Quyền

| Role | Mô tả | Quyền chính |
|---|---|---|
| `quan_ly` | Quản lý | Quản lý user, nhân viên, phòng ban, danh mục, xem báo cáo |
| `le_tan` | Lễ tân / nhân viên | Quản lý khách hàng, phòng, booking, dịch vụ, hóa đơn |
| Guest | Chưa đăng nhập | Đăng ký tài khoản, đăng nhập vào hệ thống |

Tài khoản mẫu:

| Role | Username | Password |
|---|---|---|
| `quan_ly` | `ql001` | `MyChi@123` |
| `le_tan` | `lt001` | `Chuyen@123` |
| `le_tan` | `lt002` | `DucMinh@123` |

---

## 6. Số Lượng API

Dự án có:

```text
36 endpoint
64 thao tác API theo method + endpoint
```

Thống kê theo method:

| Method | Số lượng |
|---|---:|
| GET | 25 |
| POST | 13 |
| PUT | 17 |
| DELETE | 9 |
| Tổng | 64 |

Postman collection tập trung vào **12 API theo luồng nghiệp vụ chính** để chụp hình và đưa vào báo cáo.

---

## 7. Full Danh Sách API

### 7.1. Auth

| Method | Endpoint | Chức năng |
|---|---|---|
| POST | `/api/auth/register/` | Đăng ký tài khoản lễ tân, chờ quản lý duyệt |
| POST | `/api/auth/login/` | Đăng nhập |
| POST | `/api/auth/logout/` | Đăng xuất |
| GET | `/api/auth/profile/` | Xem hồ sơ cá nhân |
| PUT | `/api/auth/profile/` | Cập nhật hồ sơ cá nhân |
| PUT | `/api/auth/change-password/` | Đổi mật khẩu |

### 7.2. User

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/users/` | Xem danh sách tài khoản |
| POST | `/api/users/` | Tạo tài khoản |
| GET | `/api/users/<id>/` | Xem chi tiết tài khoản |
| PUT | `/api/users/<id>/` | Cập nhật tài khoản |
| DELETE | `/api/users/<id>/` | Vô hiệu hóa tài khoản |

### 7.3. Department

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/departments/` | Xem danh sách phòng ban |
| POST | `/api/departments/` | Thêm phòng ban |
| GET | `/api/departments/<id>/` | Xem chi tiết phòng ban |
| PUT | `/api/departments/<id>/` | Cập nhật phòng ban |
| DELETE | `/api/departments/<id>/` | Xóa phòng ban |

### 7.4. Employee

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/employees/` | Xem danh sách nhân viên |
| POST | `/api/employees/` | Thêm nhân viên |
| GET | `/api/employees/<id>/` | Xem chi tiết nhân viên |
| PUT | `/api/employees/<id>/` | Cập nhật nhân viên |
| DELETE | `/api/employees/<id>/` | Vô hiệu hóa nhân viên |

### 7.5. Customer

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/customers/` | Xem danh sách khách hàng |
| GET | `/api/customers/?customer_type=vip` | Lọc khách VIP |
| GET | `/api/customers/?phone=0901` | Tìm khách theo số điện thoại |
| POST | `/api/customers/` | Thêm khách hàng |
| GET | `/api/customers/<id>/` | Xem chi tiết khách hàng |
| PUT | `/api/customers/<id>/` | Cập nhật khách hàng |
| DELETE | `/api/customers/<id>/` | Xóa khách hàng |

### 7.6. Room Type

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/room-types/` | Xem danh sách loại phòng |
| POST | `/api/room-types/` | Thêm loại phòng |
| GET | `/api/room-types/<id>/` | Xem chi tiết loại phòng |
| PUT | `/api/room-types/<id>/` | Cập nhật loại phòng |
| DELETE | `/api/room-types/<id>/` | Xóa loại phòng |

### 7.7. Room

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/rooms/` | Xem danh sách phòng |
| GET | `/api/rooms/?status=trong` | Lọc phòng theo trạng thái |
| POST | `/api/rooms/` | Thêm phòng |
| GET | `/api/rooms/<id>/` | Xem chi tiết phòng |
| PUT | `/api/rooms/<id>/` | Cập nhật phòng |
| DELETE | `/api/rooms/<id>/` | Xóa phòng |
| PUT | `/api/rooms/<id>/status/` | Cập nhật trạng thái phòng |

### 7.8. Service

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/services/` | Xem danh sách dịch vụ |
| POST | `/api/services/` | Thêm dịch vụ |
| GET | `/api/services/<id>/` | Xem chi tiết dịch vụ |
| PUT | `/api/services/<id>/` | Cập nhật dịch vụ |
| DELETE | `/api/services/<id>/` | Xóa mềm dịch vụ |

### 7.9. Booking

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/bookings/` | Xem danh sách đặt phòng |
| GET | `/api/bookings/?status=cho_xac_nhan` | Lọc booking theo trạng thái |
| POST | `/api/bookings/` | Tạo đặt phòng |
| GET | `/api/bookings/<id>/` | Xem chi tiết đặt phòng |
| PUT | `/api/bookings/<id>/` | Cập nhật ghi chú đặt phòng |
| DELETE | `/api/bookings/<id>/` | Hủy đặt phòng |
| PUT | `/api/bookings/<id>/confirm/` | Xác nhận đặt phòng |
| PUT | `/api/bookings/<id>/cancel/` | Hủy đặt phòng |
| PUT | `/api/bookings/<id>/check-in/` | Check-in |
| PUT | `/api/bookings/<id>/check-out/` | Check-out |
| GET | `/api/bookings/<id>/services/` | Xem dịch vụ của booking |
| POST | `/api/bookings/<id>/services/` | Thêm dịch vụ cho booking |
| GET | `/api/bookings/<id>/invoice/` | Xem hóa đơn theo booking |

### 7.10. Booking Service

| Method | Endpoint | Chức năng |
|---|---|---|
| PUT | `/api/booking-services/<id>/` | Cập nhật số lượng dịch vụ |
| DELETE | `/api/booking-services/<id>/` | Xóa dịch vụ khỏi booking |

### 7.11. Invoice

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/invoices/` | Xem danh sách hóa đơn |
| POST | `/api/invoices/` | Tạo hóa đơn thủ công |
| GET | `/api/invoices/<id>/` | Xem chi tiết hóa đơn |
| PUT | `/api/invoices/<id>/pay/` | Thanh toán hóa đơn |

### 7.12. Report

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/reports/revenue/` | Thống kê doanh thu |
| GET | `/api/reports/revenue/?tu_ngay=2026-05-01&den_ngay=2026-05-31` | Thống kê doanh thu theo ngày |
| GET | `/api/reports/room-status/` | Thống kê tình trạng phòng |
| GET | `/api/reports/booking-statistics/` | Thống kê đặt phòng |
| GET | `/api/reports/booking-statistics/?tu_ngay=2026-05-01&den_ngay=2026-05-31` | Thống kê đặt phòng theo ngày |
| GET | `/api/reports/top-services/` | Thống kê dịch vụ sử dụng nhiều |
| GET | `/api/reports/top-services/?top=3` | Top N dịch vụ |

---

## 8. Kịch Bản Postman 12 API Chính

| Bước | Method | Endpoint | Chức năng |
|---:|---|---|---|
| 1 | POST | `/api/auth/login/` | Đăng nhập |
| 2 | GET | `/api/rooms/?status=trong` | Tìm phòng trống |
| 3 | POST | `/api/customers/` | Thêm khách hàng |
| 4 | POST | `/api/bookings/` | Tạo đặt phòng |
| 5 | PUT | `/api/bookings/<id>/confirm/` | Xác nhận đặt phòng |
| 6 | PUT | `/api/bookings/<id>/check-in/` | Check-in |
| 7 | POST | `/api/bookings/<id>/services/` | Ghi nhận dịch vụ khách sử dụng |
| 8 | PUT | `/api/bookings/<id>/check-out/` | Check-out |
| 9 | GET | `/api/bookings/<id>/invoice/` | Xem hóa đơn theo đặt phòng |
| 10 | PUT | `/api/invoices/<id>/pay/` | Thanh toán hóa đơn |
| 11 | GET | `/api/reports/revenue/` | Thống kê doanh thu |
| 12 | POST | `/api/auth/logout/` | Đăng xuất |

---

## 9. Luồng Nghiệp Vụ Demo Chính

Luồng nên demo bằng Postman:

```text
1. Đăng nhập
2. Xem phòng trống
3. Thêm khách hàng
4. Tạo đặt phòng
5. Xác nhận đặt phòng
6. Check-in
7. Ghi nhận dịch vụ
8. Check-out
9. Xem hóa đơn
10. Thanh toán hóa đơn
11. Xem thống kê doanh thu
12. Đăng xuất
```

Luồng này thể hiện đủ quy trình khách sạn:

```text
tìm phòng -> đặt phòng -> nhận phòng -> dùng dịch vụ -> trả phòng -> thanh toán -> thống kê
```

---

## 10. Cài Đặt Môi Trường

```bash
pip install -r requirements.txt
```

File `requirements.txt`:

```text
django>=4.2
mysqlclient>=2.2
```

---

## 11. Tạo Database Và Dữ Liệu Mẫu

Cách 1: Chạy script SQL trong MySQL Workbench:

```text
scripts/script_create_db_hotel_management.sql
scripts/script_insert_data_hotel_management.sql
```

Cách 2: Dùng Django migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

Nếu dùng session đăng nhập, cần đảm bảo bảng `django_session` đã được tạo:

```bash
python manage.py migrate sessions
```

---

## 12. Cấu Hình Database

Kiểm tra file:

```text
hotel_management/settings.py
```

Phần database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hotel_management',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

Nếu máy khác có mật khẩu MySQL khác, sửa lại `PASSWORD`.

---

## 13. Chạy Server

```bash
cd /d E:\DA_Python\Nhom04_Code\hotel_management
python manage.py runserver 127.0.0.1:8000 --noreload
```

Base URL:

```text
http://127.0.0.1:8000
```

Base API:

```text
http://127.0.0.1:8000/api/
```

Khi test bằng Postman, phải giữ terminal đang chạy server. Nếu tắt terminal, Postman sẽ báo:

```text
ECONNREFUSED 127.0.0.1:8000
```

---

## 14. Kiểm Thử Bằng Postman

File collection:

```text
postman/hotel_management_postman_collection.json
```

Cách dùng:

1. Import file JSON vào Postman.
2. Kiểm tra collection variable:

```text
base_url = http://127.0.0.1:8000
```

3. Chạy request:

```text
01 - Dang nhap he thong
```

4. Sau khi đăng nhập thành công, chạy các API còn lại.

---

## 15. Body Mẫu

Đăng nhập:

```json
{
  "username": "ql001",
  "password": "MyChi@123"
}
```

Thêm khách hàng:

```json
{
  "full_name": "Khach Hang Postman",
  "phone": "0911999001",
  "email": "postman.customer@hotel.vn",
  "id_card": "079206099001",
  "address": "TP. Ho Chi Minh",
  "customer_type": "regular"
}
```

Tạo đặt phòng:

```json
{
  "customer_id": 1,
  "room_id": 16,
  "check_in": "2028-08-10",
  "check_out": "2028-08-13",
  "note": "Dat phong bang Postman"
}
```

Thêm dịch vụ cho booking:

```json
{
  "service_id": 1,
  "quantity": 2
}
```

Thanh toán hóa đơn:

```json
{
  "payment_method": "chuyen_khoan"
}
```

---

## 16. Chạy Unit Test

```bash
python manage.py test
```

Kết quả đã kiểm tra:

```text
Found 117 test(s)
Ran 117 tests
OK
```

---

## 17. Ghi Chú Khi Nộp Bài

Theo yêu cầu môn học, các sản phẩm cần nộp gồm:

| Sản phẩm | Ghi chú |
|---|---|
| File báo cáo Word | Theo mẫu của thầy |
| File báo cáo PDF | Xuất từ file Word |
| Source code | Nộp code dự án |
| Slide thuyết trình | Trình bày ngắn gọn, rõ ràng |
| Video thuyết trình/demo | Quay màn hình, thấy mặt thành viên |

Nếu file lớn hơn giới hạn upload, đưa link Google Drive và bật quyền:

```text
Anyone with the link can view/download
```

---

## 18. Ghi Chú Kỹ Thuật

- Project dùng session để lưu trạng thái đăng nhập.
- API cần đăng nhập sẽ trả `401` nếu chưa login.
- API cần quyền quản lý sẽ trả `403` nếu sai role.
- Password đang lưu trực tiếp để đơn giản cho đồ án môn học.
- Tiền tệ trong hệ thống tính bằng VND.
