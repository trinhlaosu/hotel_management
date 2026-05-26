# Theo Dõi Dự Án Nhóm 04

File này dùng để theo dõi kịch bản demo, trạng thái hoàn thành và các việc cần làm trước khi nộp bài. README chỉ giữ phần giới thiệu tổng quan dự án.

## 1. Trạng Thái Tổng Quan

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Source code backend API | Hoàn thành | Django REST Framework, MySQL |
| Module pricing nâng cao | Hoàn thành | App riêng `pricing`, API tính giá booking dự kiến từ dữ liệu Room/RoomType |
| Database | Hoàn thành | 10 bảng nghiệp vụ chính |
| Migration | Hoàn thành | `hotel.0001`, `0002`, `0003` đã apply |
| Authentication | Hoàn thành | Đăng ký, đăng nhập, đăng xuất, profile, đổi mật khẩu |
| Phân quyền | Hoàn thành | `quan_ly`, `le_tan`, guest |
| CRUD danh mục | Hoàn thành | User, Department, Employee, Customer, RoomType, Room, Service |
| Booking workflow | Hoàn thành | Tạo, xác nhận, hủy, check-in, check-out |
| Dịch vụ theo booking | Hoàn thành | Thêm, cập nhật, xóa dịch vụ |
| Hóa đơn | Hoàn thành | Tạo hóa đơn, xem hóa đơn, thanh toán |
| Báo cáo | Hoàn thành | Doanh thu, trạng thái phòng, thống kê booking, top dịch vụ |
| Unit/API tests | Hoàn thành | `hotel_app/tests/unit/`: kiểm tra model, service, core utility, API, phân quyền và lỗi |
| E2E script DB thật | Hoàn thành | `full_api/test_e2e_api.py` chạy full API action và `booking_flow/test_e2e_booking_flow_db.py` chạy booking flow, sinh báo cáo HTML trong từng folder riêng |
| Tổng test tự động | Hoàn thành | 140 tests OK |
| Postman collection | Hoàn thành | `docs/hotel_management_postman_collection.json` |
| Kịch bản demo full API | Hoàn thành | `docs/Nhom04_Kich_ban_demo_full_api.md`, đi qua hầu hết nhóm API chính |
| Báo cáo Word | Cần cập nhật | Đã có tên/MSSV; cần rà phân công và bổ sung ảnh Postman thật |
| Báo cáo PDF | Chưa có trong repo | Xuất từ Word sau khi hoàn tất |
| Slide thuyết trình | Chưa có trong repo | Cần tạo file `.pptx` |
| Video demo | Chưa có trong repo | Cần quay màn hình, thấy mặt thành viên |

## 2. Checklist Theo Hướng Dẫn Môn Học

| Yêu cầu | Đã đáp ứng | Minh chứng |
|---|---|---|
| Dùng Python | Có | Source code Django |
| Chủ đề Web API / Backend API Server | Có | API trong `/api/` |
| Không cần frontend | Có | Kiểm thử bằng Postman |
| Có CSDL | Có | MySQL `hotel_management` |
| Số bảng từ 5 đến 10 | Có | 10 bảng chính |
| Có tối thiểu 2 loại user | Có | `quan_ly`, `le_tan` |
| Có API login/register | Có | `/api/auth/login/`, `/api/auth/register/` |
| Có REST GET/POST/PUT/DELETE | Có | ViewSet + Router |
| Có chức năng quan trọng | Có | Booking, invoice, report |
| Có Postman | Có | Collection trong `docs/` |
| Có OOP | Có | Model, Serializer, ViewSet, Service class |
| Có MVT/MVC | Có | Django MVT |
| Có báo cáo Word | Có, cần cập nhật | `docs/Nhom04_Bao_cao.docx` |
| Có báo cáo PDF | Chưa xác nhận | Cần xuất file PDF |
| Có slide | Chưa xác nhận | Cần tạo slide |
| Có video | Chưa xác nhận | Cần quay/nộp video |

## 3. Kịch Bản Demo Postman Đề Xuất

Luồng này thể hiện trọn nghiệp vụ khách sạn từ đăng nhập đến thanh toán và báo cáo.

| Bước | Method | Endpoint | Mục tiêu |
|---:|---|---|---|
| 1 | POST | `/api/auth/login/` | Đăng nhập bằng tài khoản quản lý hoặc lễ tân |
| 2 | GET | `/api/rooms/?status=trong` | Xem danh sách phòng trống |
| 3 | POST | `/api/customers/` | Tạo khách hàng mới |
| 4 | POST | `/api/bookings/` | Tạo đặt phòng |
| 5 | PUT | `/api/bookings/<id>/confirm/` | Xác nhận đặt phòng |
| 6 | PUT | `/api/bookings/<id>/check-in/` | Check-in, phòng chuyển sang có khách |
| 7 | POST | `/api/bookings/<id>/services/` | Ghi nhận dịch vụ khách sử dụng |
| 8 | PUT | `/api/bookings/<id>/check-out/` | Check-out, phòng trở lại trống |
| 9 | GET | `/api/bookings/<id>/invoice/` | Xem hóa đơn của booking |
| 10 | PUT | `/api/invoices/<id>/pay/` | Thanh toán hóa đơn |
| 11 | GET | `/api/reports/revenue/` | Xem thống kê doanh thu |
| 12 | POST | `/api/auth/logout/` | Đăng xuất |

## 4. Body Mẫu Khi Demo

### Đăng Nhập

```json
{
  "username": "ql001",
  "password": "MyChi@123"
}
```

### Tạo Khách Hàng

```json
{
  "full_name": "Khach Hang Demo",
  "phone": "0911999001",
  "email": "demo.customer@hotel.vn",
  "id_card": "079206099001",
  "address": "TP. Ho Chi Minh",
  "customer_type": "regular"
}
```

### Tạo Booking

```json
{
  "customer_id": 1,
  "room_id": 16,
  "check_in": "2028-08-10",
  "check_out": "2028-08-13",
  "note": "Dat phong bang Postman"
}
```

### Thêm Dịch Vụ Cho Booking

```json
{
  "service_id": 1,
  "quantity": 2
}
```

### Thanh Toán Hóa Đơn

```json
{
  "payment_method": "chuyen_khoan"
}
```

## 5. Việc Cần Làm Trước Khi Nộp

| Việc cần làm | Trạng thái | Ghi chú |
|---|---|---|
| Cập nhật tên thành viên, MSSV trong báo cáo | Xong | Đã thêm 3 thành viên nhóm |
| Cập nhật phân công công việc thật | Cần rà lại | Đang có bản phân công đề xuất, cần nhóm xác nhận |
| Chụp ảnh Postman thật đưa vào báo cáo | Chưa xong | Login, booking, service, invoice, report |
| Xuất báo cáo Word sang PDF | Chưa xong | Nộp cả `.docx` và `.pdf` |
| Tạo slide thuyết trình | Chưa xong | Giới thiệu, CSDL, kiến trúc, chức năng, kết quả |
| Quay video demo | Chưa xong | Quay màn hình, thấy mặt thành viên |
| Kiểm tra lại Postman collection | Cần kiểm tra | Chạy đủ luồng trước khi quay |
| Chạy lại test lần cuối | Xong gần nhất | 140 tests OK |
| Chạy E2E DB thật lần cuối | Xong gần nhất | `full_api/bao_cao_e2e_api.html` có 91 bước PASS; `booking_flow/bao_cao_e2e_booking_flow.html` PASS |

## 6. Ghi Chú Khi Quay Video

- Nên demo ngắn gọn theo luồng 12 bước ở trên.
- Mở server Django trước khi quay.
- Mở Postman collection và chạy request theo thứ tự.
- Video cần thấy mặt thành viên nếu nộp hệ trực tuyến.
- Nếu theo hướng dẫn 5 phút thì ưu tiên demo các bước quan trọng nhất; nếu theo buổi hướng dẫn 15 phút thì có thể trình bày thêm kiến trúc và CSDL.

## 7. Lệnh Kiểm Tra Nhanh

```bash
python manage.py check
python manage.py test
python hotel_app/tests/e2e/full_api/test_e2e_api.py --prefix demo01
python hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py --prefix bookdemo01
python manage.py showmigrations hotel
python manage.py runserver 127.0.0.1:8000
```

Kết quả gần nhất:

```text
python manage.py check -> OK
python manage.py test -> 140 tests OK
E2E DB thật -> full_api/bao_cao_e2e_api.html 91 bước PASS; booking_flow/bao_cao_e2e_booking_flow.html PASS
hotel migrations -> 0001, 0002, 0003 đã apply
```
