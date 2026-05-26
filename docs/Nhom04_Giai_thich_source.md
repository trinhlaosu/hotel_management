# Giải Thích Source Code Dự Án

Tài liệu này giải thích cách đọc source code từ đầu đến cuối và luồng xử lý của từng nhóm chức năng trong hệ thống RESTful API quản lý khách sạn.

## 1. Điểm Bắt Đầu Của Project

Khi chạy server:

```bash
python manage.py runserver
```

Django bắt đầu từ:

```text
manage.py
```

File này nạp cấu hình:

```text
config/settings.py
```

Trong `settings.py`, project khai báo app chính, database MySQL, Django REST Framework, authentication custom, permission mặc định, pagination và exception handler.

Sau đó Django đọc URL gốc:

```text
config/urls.py
```

File này dẫn request `/api/` vào:

```text
hotel_app/urls.py
```

Trong `hotel_app/urls.py`, DRF router đăng ký các nhóm API:

```text
auth
users
departments
employees
customers
room-types
rooms
services
bookings
booking-services
invoices
reports
```

## 2. Luồng Chung Của Một API

Ví dụ client gọi:

```text
POST /api/bookings/
```

Luồng xử lý:

```text
Client/Postman
-> config/urls.py
-> hotel_app/urls.py
-> hotel_app/views/bookings.py
-> hotel_app/serializers/bookings.py
-> hotel_app/services/booking_service.py
-> hotel_app/models.py
-> database MySQL
-> response JSON
```

Vai trò từng lớp:

| Lớp | Vai trò |
|---|---|
| `models.py` | Định nghĩa bảng database và quan hệ |
| `serializers/` | Validate input và format output |
| `views/` | Nhận request, gọi serializer/service, trả response |
| `services/` | Xử lý nghiệp vụ chính |
| `core/` | Response, message, exception, field dùng chung |

## 3. Chức Năng Auth

File chính:

```text
hotel_app/views/auth.py
hotel_app/serializers/auth.py
hotel_app/services/auth_service.py
hotel_app/authentication.py
hotel_app/permissions.py
core/messages.py
```

API:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/profile/
PUT  /api/auth/profile/
PUT  /api/auth/change-password/
```

Luồng login:

```text
auth.py nhận username/password
-> LoginSerializer kiểm tra dữ liệu
-> AuthService.dang_nhap()
-> kiểm tra User có active không
-> kiểm tra mật khẩu bằng check_password()
-> lưu user_id và role vào session
-> trả JSON
```

`authentication.py` lấy user hiện tại từ session:

```text
request.session["user_id"]
```

`permissions.py` kiểm tra người dùng đã đăng nhập chưa và có phải quản lý hay không.

## 4. Chức Năng User

File chính:

```text
hotel_app/views/users.py
hotel_app/serializers/users.py
hotel_app/services/user_service.py
hotel_app/models.py
```

API:

```text
GET    /api/users/
POST   /api/users/
GET    /api/users/<id>/
PUT    /api/users/<id>/
DELETE /api/users/<id>/
POST   /api/users/<id>/disable/
POST   /api/users/<id>/enable/
```

Chỉ `quan_ly` được quản lý user.

Khi tạo user:

```text
UserCreateSerializer validate username/email/password
-> hash password bằng make_password()
-> lưu User
```

Khi xóa user:

```text
UserService.disable()
-> is_active = False
```

User không bị xóa khỏi database mà chỉ bị vô hiệu hóa.

## 5. Chức Năng Department

File chính:

```text
hotel_app/views/departments.py
hotel_app/serializers/departments.py
hotel_app/models.py
```

API:

```text
GET    /api/departments/
POST   /api/departments/
GET    /api/departments/<id>/
PUT    /api/departments/<id>/
DELETE /api/departments/<id>/
```

Quyền:

```text
Xem: người dùng đã đăng nhập
Tạo/sửa/xóa: quan_ly
```

Serializer kiểm tra tên phòng ban không trùng.

DELETE dùng soft delete:

```text
is_deleted = True
```

## 6. Chức Năng Employee

File chính:

```text
hotel_app/views/employees.py
hotel_app/serializers/employees.py
hotel_app/services/employee_service.py
hotel_app/models.py
```

API:

```text
GET    /api/employees/
POST   /api/employees/
GET    /api/employees/<id>/
PUT    /api/employees/<id>/
DELETE /api/employees/<id>/
```

Khi tạo employee:

```text
EmployeeCreateSerializer
-> tạo User trước
-> password được hash
-> role = le_tan
-> tạo Employee gắn với User
```

Khi xóa employee:

```text
EmployeeService.disable()
-> employee.status = nghi_viec
-> employee.user.is_active = False
```

Nhân viên không bị xóa khỏi database, chỉ chuyển sang nghỉ việc và khóa tài khoản.

## 7. Chức Năng Customer

File chính:

```text
hotel_app/views/customers.py
hotel_app/serializers/customers.py
hotel_app/models.py
```

API:

```text
GET    /api/customers/
POST   /api/customers/
GET    /api/customers/<id>/
PUT    /api/customers/<id>/
DELETE /api/customers/<id>/
```

Serializer kiểm tra:

```text
Số điện thoại không trùng
CCCD không trùng
```

DELETE dùng soft delete:

```text
is_deleted = True
```

## 8. Chức Năng Room Type Và Room

File chính:

```text
hotel_app/views/rooms.py
hotel_app/serializers/rooms.py
hotel_app/services/room_service.py
hotel_app/models.py
```

RoomType API:

```text
GET    /api/room-types/
POST   /api/room-types/
GET    /api/room-types/<id>/
PUT    /api/room-types/<id>/
DELETE /api/room-types/<id>/
```

Room API:

```text
GET    /api/rooms/
POST   /api/rooms/
GET    /api/rooms/<id>/
PUT    /api/rooms/<id>/
DELETE /api/rooms/<id>/
PUT    /api/rooms/<id>/status/
```

`RoomService` xử lý:

```text
Kiểm tra phòng có trống không
Cập nhật trạng thái phòng
Thống kê phòng
```

Trạng thái phòng:

```text
trong
co_khach
bao_tri
```

## 9. Chức Năng Service

File chính:

```text
hotel_app/views/services.py
hotel_app/serializers/services.py
hotel_app/services/service_service.py
hotel_app/models.py
```

API dịch vụ:

```text
GET    /api/services/
POST   /api/services/
GET    /api/services/<id>/
PUT    /api/services/<id>/
DELETE /api/services/<id>/
```

DELETE service:

```text
is_active = False
```

Danh sách `/api/services/` chỉ hiện service đang active.

## 10. Chức Năng Booking

File chính:

```text
hotel_app/views/bookings.py
hotel_app/serializers/bookings.py
hotel_app/services/booking_service.py
hotel_app/services/room_service.py
hotel_app/services/invoice_service.py
hotel_app/models.py
```

API:

```text
GET    /api/bookings/
POST   /api/bookings/
GET    /api/bookings/<id>/
PUT    /api/bookings/<id>/
DELETE /api/bookings/<id>/
PUT    /api/bookings/<id>/confirm/
PUT    /api/bookings/<id>/cancel/
PUT    /api/bookings/<id>/check-in/
PUT    /api/bookings/<id>/check-out/
GET    /api/bookings/<id>/services/
POST   /api/bookings/<id>/services/
GET    /api/bookings/<id>/invoice/
```

Luồng tạo booking:

```text
BookingViewSet.create()
-> BookingCreateSerializer validate customer_id, room_id, ngày check_in/check_out
-> kiểm tra check_out > check_in
-> kiểm tra trùng lịch phòng
-> BookingService.tao_booking_va_hoa_don()
-> tạo Booking
-> tạo Invoice ban đầu
-> trả booking_id, tiền phòng, tổng tiền
```

Trạng thái booking:

```text
cho_xac_nhan
da_xac_nhan
dang_o
da_tra_phong
da_huy
```

Luồng booking chuẩn:

```text
cho_xac_nhan
-> confirm
-> da_xac_nhan
-> check-in
-> dang_o
-> check-out
-> da_tra_phong
```

Khi check-in:

```text
booking.status = dang_o
room.status = co_khach
```

Khi check-out:

```text
booking.status = da_tra_phong
room.status = trong
invoice được cập nhật lại
```

## 11. Chức Năng Booking Service

File chính:

```text
hotel_app/views/services.py
hotel_app/views/bookings.py
hotel_app/serializers/bookings.py
hotel_app/services/service_service.py
hotel_app/services/invoice_service.py
hotel_app/models.py
```

API:

```text
POST   /api/bookings/<id>/services/
GET    /api/bookings/<id>/services/
PUT    /api/booking-services/<id>/
DELETE /api/booking-services/<id>/
```

Khi thêm dịch vụ vào booking:

```text
kiểm tra booking tồn tại
-> kiểm tra service tồn tại
-> kiểm tra quantity > 0
-> tạo BookingService
-> subtotal = service.price * quantity
-> cập nhật lại hóa đơn
```

Khi sửa số lượng:

```text
cập nhật quantity
-> tính lại subtotal
-> cập nhật lại hóa đơn
```

Khi xóa dịch vụ khỏi booking:

```text
xóa BookingService
-> cập nhật lại hóa đơn
```

## 12. Chức Năng Invoice

File chính:

```text
hotel_app/views/invoices.py
hotel_app/serializers/invoices.py
hotel_app/services/invoice_service.py
hotel_app/models.py
```

API:

```text
GET  /api/invoices/
POST /api/invoices/
GET  /api/invoices/<id>/
PUT  /api/invoices/<id>/pay/
```

`InvoiceService` xử lý:

```text
tính số đêm
-> tiền phòng = số đêm * giá phòng
-> tiền dịch vụ = tổng subtotal của BookingService
-> total = tiền phòng + tiền dịch vụ
```

Khi thanh toán:

```text
payment_status = da_thanh_toan
payment_method = tien_mat / chuyen_khoan / the
paid_at = thời gian hiện tại
```

## 13. Chức Năng Report

File chính:

```text
hotel_app/views/reports.py
hotel_app/services/report_service.py
hotel_app/models.py
```

API:

```text
GET /api/reports/revenue/
GET /api/reports/room-status/
GET /api/reports/booking-statistics/
GET /api/reports/top-services/
```

Chỉ `quan_ly` được xem báo cáo.

Các báo cáo:

```text
revenue              doanh thu từ hóa đơn đã thanh toán
room-status          số phòng trống/có khách/bảo trì
booking-statistics   thống kê booking theo trạng thái
top-services         dịch vụ được dùng nhiều nhất
```

## 14. Core Dùng Chung

File chính:

```text
core/api.py
core/messages.py
core/exceptions.py
core/fields.py
core/utils.py
core/validators.py
```

`core/messages.py` chứa toàn bộ message trả về API bằng tiếng Việt có dấu.

`core/api.py` chứa:

```text
api_response()
serializer_error_response()
ApiResponseModelViewSet
```

`ApiResponseModelViewSet` giúp các view CRUD trả response thống nhất:

```json
{
  "message": "...",
  "data": {}
}
```

`core/exceptions.py` format lỗi DRF thành:

```json
{
  "error": "..."
}
```

`core/fields.py` chứa `NotFoundPrimaryKeyRelatedField`, giúp ID không tồn tại trả lỗi 404 thay vì validation thường.

## 15. Tests

Tests được chia thành hai nhóm:

```text
hotel_app/tests/unit/
hotel_app/tests/e2e/
```

Unit/API test:

```text
test_core.py
test_models.py
test_services.py
test_views_auth_users.py
test_views_bookings_services.py
test_views_customers_rooms.py
test_views_full_api.py
test_views_invoices_reports.py
```

E2E test:

```text
test_e2e_booking_flow.py
```

E2E test chạy trọn luồng:

```text
login
-> xem phòng trống
-> tạo khách hàng
-> tạo booking
-> confirm
-> check-in
-> thêm dịch vụ
-> check-out
-> xem hóa đơn
-> thanh toán
-> xem báo cáo
```

Hiện tại:

```text
137 tests OK
```

## 16. Luồng Quan Trọng Nhất

Nếu cần trình bày ngắn gọn chức năng chính của hệ thống:

```text
Người dùng đăng nhập.
Lễ tân tạo khách hàng và đặt phòng.
Hệ thống kiểm tra phòng có bị trùng lịch không.
Sau khi xác nhận, khách check-in, phòng chuyển sang có khách.
Trong thời gian ở, lễ tân thêm dịch vụ cho booking.
Hệ thống tự tính lại hóa đơn.
Khi check-out, phòng trở lại trống.
Khách thanh toán hóa đơn.
Quản lý xem báo cáo doanh thu.
```
