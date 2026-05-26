# Xây Dựng RESTful API Quản Lý Khách Sạn

**Nhóm 04 - Đồ án môn học Lập trình Python**

| Thành viên | MSSV |
|---|---|
| Trịnh Thị Mỹ Chi | 25410022 |
| Võ Mộng Chuyền | 25410024 |
| Lê Đức Minh | 25410092 |

Dự án xây dựng **RESTful API Server** cho nghiệp vụ quản lý khách sạn. Hệ thống tập trung vào backend API, không xây dựng frontend riêng; các chức năng được kiểm thử và minh họa bằng Postman.

## 1. Mục Tiêu Dự Án

Hệ thống hỗ trợ các nghiệp vụ chính của khách sạn:

- Quản lý tài khoản người dùng và phân quyền.
- Quản lý phòng ban, nhân viên, khách hàng.
- Quản lý loại phòng, phòng và trạng thái phòng.
- Quản lý dịch vụ khách sạn.
- Tạo đặt phòng, xác nhận, hủy, check-in, check-out.
- Ghi nhận dịch vụ sử dụng theo từng booking.
- Lập hóa đơn, thanh toán hóa đơn.
- Thống kê doanh thu, trạng thái phòng, booking và dịch vụ được sử dụng nhiều.

## 2. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python |
| Framework | Django |
| API framework | Django REST Framework |
| Database | MySQL |
| Filter/Search | django-filter |
| Kiến trúc | Django MVT kết hợp service layer |
| Kiểm thử | Unit/API test, E2E test, E2E script trên DB thật, Postman |

## 3. Điểm Chính Của Dự Án

- Source code được xây dựng bằng Python, Django REST Framework; tổ chức theo Django MVT kết hợp service layer và tập trung vào RESTful API Server, không xây dựng frontend riêng.
- View được viết dưới dạng class-based ViewSet; các nghiệp vụ quan trọng như đặt phòng, phòng, hóa đơn và báo cáo được gọi sang module service riêng thay vì xử lý trực tiếp trong view.
- Project có nhiều app/module: `hotel_app` xử lý nghiệp vụ khách sạn chính, `pricing` là module nâng cao dùng để tính giá booking dự kiến.
- Cơ sở dữ liệu sử dụng MySQL với 10 bảng nghiệp vụ chính.
- Hệ thống có các vai trò người dùng: `quan_ly`, `le_tan` và guest; phân quyền theo vai trò, không để mọi API đều truy cập tự do.
- Có API đăng ký, đăng nhập, đăng xuất và quản lý hồ sơ cá nhân.
- Có đầy đủ các nhóm REST API dùng `GET`, `POST`, `PUT`, `DELETE`.
- Có luồng nghiệp vụ hoàn chỉnh: tìm phòng -> đặt phòng -> xác nhận -> check-in -> sử dụng dịch vụ -> check-out -> thanh toán -> thống kê.
- Có kiểm tra trùng lịch đặt phòng, tránh đặt cùng một phòng trong cùng khoảng thời gian.
- Mật khẩu được mã hóa bằng Django password hasher, không lưu plain text.
- Có soft delete hoặc vô hiệu hóa dữ liệu quan trọng để giữ lịch sử hệ thống.
- Có API báo cáo doanh thu, trạng thái phòng, thống kê booking và top dịch vụ.
- Có API nâng cao `/api/pricing/calculate-booking-price/`: app chính gọi sang module `pricing` để tính giá booking dự kiến.
- Kiểm thử được tách thành Unit/API test và E2E script chạy trên database thật; 140 test tự động chạy thành công, report E2E API có 91 bước PASS.
- Có Postman collection để kiểm thử thủ công và demo API.
- Các thành phần chính được triển khai theo hướng đối tượng qua model, serializer, viewset và service class.

## 4. Kiến Trúc Hệ Thống

Dự án áp dụng mô hình **Django MVT**:

| Lớp | Thành phần trong dự án | Vai trò |
|---|---|---|
| Model | `hotel_app/models.py` | Định nghĩa bảng, quan hệ, ràng buộc dữ liệu |
| View | `hotel_app/views/` | Class-based ViewSet, nhận request, kiểm tra quyền, gọi serializer/service, trả response |
| Template/Representation | `hotel_app/serializers/`, `core/api.py` | Validate dữ liệu và biểu diễn response JSON |
| Service | `hotel_app/services/` | Xử lý nghiệp vụ quan trọng như booking, trạng thái phòng, hóa đơn, báo cáo |
| Module nâng cao | `pricing/` | Tính giá booking từ dữ liệu Room/RoomType của app chính |
| Router | `hotel_app/urls.py` | Đăng ký endpoint API |

Luồng xử lý tổng quát:

```text
Client/Postman
  -> URL Router
  -> ViewSet
  -> Serializer
  -> Service
  -> Model/Database
  -> JSON Response
```

## 5. Cơ Sở Dữ Liệu

Database: `hotel_management`

Hệ thống gồm 10 bảng nghiệp vụ chính:

| STT | Bảng | Mô tả |
|---:|---|---|
| 1 | `User` | Tài khoản đăng nhập, vai trò và trạng thái hoạt động |
| 2 | `Department` | Phòng ban trong khách sạn |
| 3 | `Employee` | Hồ sơ nhân viên |
| 4 | `Customer` | Thông tin khách hàng |
| 5 | `RoomType` | Loại phòng, giá theo đêm, sức chứa |
| 6 | `Room` | Phòng cụ thể và trạng thái phòng |
| 7 | `Booking` | Thông tin đặt phòng |
| 8 | `Invoice` | Hóa đơn thanh toán |
| 9 | `Service` | Danh mục dịch vụ khách sạn |
| 10 | `BookingService` | Dịch vụ được sử dụng trong từng booking |

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

Tiền tệ trong hệ thống sử dụng **VND**.

## 6. Đối Tượng Người Dùng

| Vai trò | Mô tả | Quyền chính |
|---|---|---|
| `quan_ly` | Quản lý | Quản lý user, nhân viên, phòng ban, danh mục và xem báo cáo |
| `le_tan` | Lễ tân / nhân viên | Quản lý khách hàng, phòng, booking, dịch vụ và hóa đơn |
| Guest | Chưa đăng nhập | Đăng ký tài khoản và đăng nhập |

Tài khoản mẫu:

| Vai trò | Username | Password |
|---|---|---|
| `quan_ly` | `ql001` | `MyChi@123` |
| `le_tan` | `lt001` | `Chuyen@123` |
| `le_tan` | `lt002` | `DucMinh@123` |

## 7. Nhóm API Chính

| Nhóm API | Endpoint chính | Chức năng |
|---|---|---|
| Auth | `/api/auth/` | Đăng ký, đăng nhập, đăng xuất, hồ sơ cá nhân |
| User | `/api/users/` | Quản lý tài khoản |
| Department | `/api/departments/` | Quản lý phòng ban |
| Employee | `/api/employees/` | Quản lý nhân viên |
| Pricing | `/api/pricing/calculate-booking-price/` | API nâng cao tính giá booking dự kiến bằng module riêng |
| Customer | `/api/customers/` | Quản lý khách hàng |
| Room Type | `/api/room-types/` | Quản lý loại phòng |
| Room | `/api/rooms/` | Quản lý phòng và trạng thái phòng |
| Service | `/api/services/` | Quản lý dịch vụ |
| Booking | `/api/bookings/` | Đặt phòng và vòng đời booking |
| Booking Service | `/api/booking-services/` | Cập nhật/xóa dịch vụ trong booking |
| Invoice | `/api/invoices/` | Lập và thanh toán hóa đơn |
| Report | `/api/reports/` | Báo cáo và thống kê |

## 8. Cài Đặt Và Chạy Dự Án

Cài thư viện:

```bash
pip install -r requirements.txt
```

Tạo database MySQL tên `hotel_management`, sau đó chạy migration:

```bash
python manage.py migrate
```

Chạy server:

```bash
python manage.py runserver 127.0.0.1:8000
```

Base API:

```text
http://127.0.0.1:8000/api/
```

## 9. Kiểm Thử

Nhóm test tự động được chia thành hai phần:

| Nhóm test | Mục tiêu |
|---|---|
| Unit/API test | Nằm trong `hotel_app/tests/unit/`, kiểm tra model, service, core utility, serializer/view API, phân quyền, soft delete và các luồng lỗi quan trọng |
| E2E script trên DB thật | `e2e/full_api/test_e2e_api.py` chạy gần full API action và `e2e/booking_flow/test_e2e_booking_flow_db.py` chạy riêng booking flow, sau đó sinh file HTML báo cáo |

Chạy toàn bộ test:

```bash
python manage.py test
```

Kết quả kiểm tra hiện tại:

```text
Found 140 test(s)
Ran 140 tests
OK
```

Postman collection:

```text
docs/hotel_management_postman_collection.json
```

Chạy E2E script trên database thật và sinh báo cáo HTML:

```bash
python hotel_app/tests/e2e/full_api/test_e2e_api.py --prefix demo01
python hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py --prefix bookdemo01
```

File báo cáo sau khi chạy:

```text
hotel_app/tests/e2e/full_api/bao_cao_e2e_api.html
hotel_app/tests/e2e/booking_flow/bao_cao_e2e_booking_flow.html
```

## 10. Tài Liệu Liên Quan

- Postman collection: `docs/hotel_management_postman_collection.json`
- Script tạo database/bảng: `scripts/script_create_db_hotel_management.sql`
- Script thêm dữ liệu mẫu: `scripts/script_insert_data_hotel_management.sql`
- Kịch bản demo full API: `docs/Nhom04_Kich_ban_demo_full_api.md`
- Giải thích app pricing nâng cao: `docs/Nhom04_Giai_thich_app_pricing.md`
- E2E full API script: `hotel_app/tests/e2e/full_api/test_e2e_api.py`
- E2E booking flow script: `hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py`
- Báo cáo E2E full API: `hotel_app/tests/e2e/full_api/bao_cao_e2e_api.html`
- Báo cáo E2E booking flow: `hotel_app/tests/e2e/booking_flow/bao_cao_e2e_booking_flow.html`
