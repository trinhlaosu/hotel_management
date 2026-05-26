# Kịch Bản Demo Sử Dụng Hầu Hết API

## 1. Mục đích

File này dùng để demo đồ án theo yêu cầu: có một kịch bản chạy qua hầu hết các nhóm API chính của hệ thống.

Kịch bản phù hợp để:

- Chạy thủ công bằng Postman.
- Quay video demo.
- Trình bày với thầy khi cần chứng minh API hoạt động theo luồng nghiệp vụ.

## 2. Chuẩn bị

Chạy server:

```bash
python manage.py runserver 127.0.0.1:8000
```

Import Postman collection:

```text
docs/hotel_management_postman_collection.json
```

Tài khoản quản lý mẫu:

```text
username: ql001
password: MyChi@123
```

Tài khoản lễ tân mẫu:

```text
username: lt001
password: Chuyen@123
```

## 3. Luồng demo tổng quát

```text
Đăng nhập quản lý
-> kiểm tra tài khoản, phòng ban, nhân viên
-> tạo khách hàng
-> xem loại phòng, phòng trống, dịch vụ
-> gọi pricing để tính giá booking dự kiến
-> tạo booking
-> xác nhận booking
-> check-in
-> thêm dịch vụ vào booking
-> xem hóa đơn
-> check-out
-> thanh toán hóa đơn
-> xem báo cáo
-> đăng xuất
```

## 4. Kịch bản chi tiết

| Bước | Method | API | Mục đích |
|---:|---|---|---|
| 1 | POST | `/api/auth/login/` | Đăng nhập quản lý |
| 2 | GET | `/api/auth/profile/` | Xem hồ sơ người đang đăng nhập |
| 3 | GET | `/api/users/` | Xem danh sách tài khoản |
| 4 | POST | `/api/users/` | Tạo tài khoản lễ tân demo |
| 5 | POST | `/api/users/<id>/disable/` | Vô hiệu hóa tài khoản |
| 6 | POST | `/api/users/<id>/enable/` | Kích hoạt lại tài khoản |
| 7 | GET | `/api/departments/` | Xem danh sách phòng ban |
| 8 | POST | `/api/departments/` | Tạo phòng ban demo |
| 9 | GET | `/api/employees/` | Xem danh sách nhân viên |
| 10 | POST | `/api/employees/` | Tạo nhân viên demo |
| 11 | GET | `/api/customers/` | Xem danh sách khách hàng |
| 12 | POST | `/api/customers/` | Tạo khách hàng mới |
| 13 | GET | `/api/room-types/` | Xem loại phòng |
| 14 | GET | `/api/rooms/?status=trong` | Tìm phòng trống |
| 15 | PUT | `/api/rooms/<id>/status/` | Cập nhật trạng thái phòng nếu cần |
| 16 | GET | `/api/services/` | Xem danh sách dịch vụ |
| 17 | POST | `/api/services/` | Tạo dịch vụ demo |
| 18 | POST | `/api/pricing/calculate-booking-price/` | API nâng cao tính giá booking dự kiến |
| 19 | POST | `/api/bookings/` | Tạo booking |
| 20 | GET | `/api/bookings/<id>/` | Xem chi tiết booking |
| 21 | PUT | `/api/bookings/<id>/confirm/` | Xác nhận booking |
| 22 | PUT | `/api/bookings/<id>/check-in/` | Check-in |
| 23 | POST | `/api/bookings/<id>/services/` | Thêm dịch vụ vào booking |
| 24 | GET | `/api/bookings/<id>/services/` | Xem dịch vụ đã dùng trong booking |
| 25 | GET | `/api/bookings/<id>/invoice/` | Xem hóa đơn theo booking |
| 26 | PUT | `/api/bookings/<id>/check-out/` | Check-out |
| 27 | PUT | `/api/invoices/<id>/pay/` | Thanh toán hóa đơn |
| 28 | GET | `/api/reports/revenue/` | Xem báo cáo doanh thu |
| 29 | GET | `/api/reports/room-status/` | Xem báo cáo trạng thái phòng |
| 30 | GET | `/api/reports/booking-statistics/` | Xem thống kê booking |
| 31 | GET | `/api/reports/top-services/` | Xem top dịch vụ |
| 32 | POST | `/api/auth/logout/` | Đăng xuất |

## 5. Body mẫu cho các API quan trọng

### 5.1. Đăng nhập

```json
{
  "username": "ql001",
  "password": "MyChi@123"
}
```

### 5.2. Tạo khách hàng

```json
{
  "full_name": "Postman Demo Customer",
  "phone": "0911999001",
  "email": "demo.postman@hotel.vn",
  "id_card": "079206099001",
  "address": "TP. Hồ Chí Minh",
  "customer_type": "vip"
}
```

Khi chạy nhiều lần, cần đổi `phone` và `id_card` để không trùng dữ liệu.

### 5.3. Tính giá booking dự kiến bằng pricing

```json
{
  "room_id": 16,
  "check_in": "2028-08-10",
  "check_out": "2028-08-13",
  "customer_type": "vip"
}
```

API này thể hiện phần nâng cao: app chính dùng dữ liệu phòng, còn module `pricing` xử lý thuật toán tính giá.

### 5.4. Tạo booking

```json
{
  "customer_id": 1,
  "room_id": 16,
  "check_in": "2028-08-10",
  "check_out": "2028-08-13",
  "note": "Booking demo full API"
}
```

### 5.5. Thêm dịch vụ vào booking

```json
{
  "service_id": 1,
  "quantity": 2
}
```

### 5.6. Thanh toán hóa đơn

```json
{
  "payment_method": "chuyen_khoan"
}
```

## 6. Kịch bản nói khi demo

```text
Đầu tiên nhóm đăng nhập bằng tài khoản quản lý để lấy session.
Sau đó nhóm kiểm tra các API quản trị như user, department, employee.
Tiếp theo nhóm tạo khách hàng, tìm phòng trống và xem dịch vụ.
Trước khi tạo booking, nhóm gọi module pricing để tính giá dự kiến.
Sau đó nhóm tạo booking, xác nhận, check-in, thêm dịch vụ, xem hóa đơn, check-out và thanh toán.
Cuối cùng nhóm mở các API báo cáo để kiểm tra doanh thu, trạng thái phòng, thống kê booking và top dịch vụ.
```

## 7. Cách chạy tự động thay cho Postman

Nếu muốn chạy nhanh trên database thật và sinh báo cáo HTML:

```bash
python hotel_app/tests/e2e/full_api/test_e2e_api.py --prefix demo_full_api
```

File kết quả:

```text
hotel_app/tests/e2e/full_api/bao_cao_e2e_api.html
```

Báo cáo này hiện có 91 bước, bao gồm cả API nâng cao `pricing`.
