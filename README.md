# Xây Dựng RESTful API Quản Lý Khách Sạn

**Nhóm 04 — Đồ án môn học Lập trình Python**

| Thành viên | MSSV |
|---|---|
| Trịnh Thị Mỹ Chi | 25410022 |
| Võ Mộng Chuyền | 25410024 |
| Lê Đức Minh | 25410092 |

Dự án xây dựng **RESTful API Server** cho nghiệp vụ quản lý khách sạn bằng Python, Django và Django REST Framework. Hệ thống tập trung vào backend API; các chức năng được kiểm thử bằng Postman và bộ E2E script tự động.

---

## 1. Mục Tiêu Dự Án

Hệ thống hỗ trợ đầy đủ nghiệp vụ khách sạn:

- Quản lý tài khoản người dùng, phân quyền theo vai trò.
- Quản lý phòng ban, nhân viên, khách hàng.
- Quản lý loại phòng, phòng và trạng thái phòng.
- Quản lý danh mục dịch vụ khách sạn.
- Luồng đặt phòng hoàn chỉnh: tạo → xác nhận → check-in → sử dụng dịch vụ → check-out → thanh toán.
- Lập và thanh toán hóa đơn, theo dõi lịch sử.
- Báo cáo doanh thu, thống kê trạng thái phòng, đặt phòng và top dịch vụ.
- API nâng cao tính giá booking dự kiến với module `pricing` riêng biệt.

---

## 2. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3 |
| Framework | Django |
| API framework | Django REST Framework |
| Database | MySQL |
| Filter / Search | django-filter |
| Kiến trúc | Django MVT kết hợp Service Layer |
| Kiểm thử | Unit test, E2E script trên DB thật, Postman |

---

## 3. Kiến Trúc Hệ Thống

Dự án áp dụng mô hình **Django MVT** kết hợp **Service Layer**:

| Lớp | Thành phần | Vai trò |
|---|---|---|
| Model | `hotel_app/models.py` | Định nghĩa 10 bảng nghiệp vụ, quan hệ và ràng buộc |
| View | `hotel_app/views/` | Class-based ViewSet nhận request, kiểm tra quyền, gọi service |
| Serializer | `hotel_app/serializers/` | Validate input và định dạng JSON response |
| Service | `hotel_app/services/` | Xử lý nghiệp vụ: booking, phòng, hóa đơn, báo cáo |
| Module nâng cao | `pricing/` | Tính giá booking từ dữ liệu Room/RoomType của app chính |
| Router | `hotel_app/urls.py`, `pricing/urls.py` | Đăng ký toàn bộ endpoint API |

Luồng xử lý:

```text
Client / Postman
  → URL Router
  → ViewSet  (kiểm tra quyền)
  → Serializer  (validate input)
  → Service  (nghiệp vụ)
  → Model / Database
  → JSON Response
```

---

## 4. Cơ Sở Dữ Liệu

Database: **`hotel_management`** (MySQL) — **10 bảng nghiệp vụ**, đơn vị tiền tệ VND.

| STT | Bảng | Mô tả |
|---:|---|---|
| 1 | `User` | Tài khoản đăng nhập, vai trò (`quan_ly` / `le_tan`) |
| 2 | `Department` | Phòng ban trong khách sạn |
| 3 | `Employee` | Hồ sơ nhân viên, liên kết User |
| 4 | `Customer` | Thông tin khách hàng |
| 5 | `RoomType` | Loại phòng, giá theo đêm, sức chứa |
| 6 | `Room` | Phòng cụ thể, trạng thái (`trong` / `co_khach` / `bao_tri`) |
| 7 | `Booking` | Thông tin đặt phòng và trạng thái |
| 8 | `Invoice` | Hóa đơn thanh toán |
| 9 | `Service` | Danh mục dịch vụ khách sạn |
| 10 | `BookingService` | Dịch vụ sử dụng trong từng booking |

Quan hệ chính:

```text
User         1 — 1   Employee
Department   1 — n   Employee
RoomType     1 — n   Room
Customer     1 — n   Booking
Room         1 — n   Booking
Employee     1 — n   Booking  (created_by)
Booking      1 — 1   Invoice
Booking      1 — n   BookingService
Service      1 — n   BookingService
```

---

## 5. Đối Tượng Người Dùng

| Vai trò | Mô tả | Quyền chính |
|---|---|---|
| `quan_ly` | Quản lý | Toàn quyền: quản lý user, nhân viên, phòng ban, danh mục; xem báo cáo |
| `le_tan` | Lễ tân / Nhân viên | Quản lý khách hàng, booking, dịch vụ và hóa đơn |
| Guest | Chưa đăng nhập | Đăng ký tài khoản |

Tài khoản mẫu:

| Vai trò | Username | Password |
|---|---|---|
| `quan_ly` | `ql001` | `MyChi@123` |
| `le_tan` | `lt001` | `Chuyen@123` |
| `le_tan` | `lt002` | `DucMinh@123` |

---

## 6. Danh Sách API

Tổng cộng **77 endpoint** trên **13 nhóm tài nguyên**:

| Nhóm | Endpoint gốc | Số endpoint | Chức năng chính |
|---|---|---|---|
| Auth | `/api/auth/` | 6 | Đăng ký, đăng nhập, đăng xuất, hồ sơ, đổi mật khẩu |
| Users | `/api/users/` | 8 | CRUD + khoá/mở khoá tài khoản |
| Departments | `/api/departments/` | 6 | CRUD phòng ban |
| Employees | `/api/employees/` | 6 | CRUD nhân viên |
| Customers | `/api/customers/` | 6 | CRUD khách hàng |
| Room Types | `/api/room-types/` | 6 | CRUD loại phòng |
| Rooms | `/api/rooms/` | 7 | CRUD + đổi trạng thái phòng |
| Services | `/api/services/` | 6 | CRUD dịch vụ |
| Bookings | `/api/bookings/` | 12 | Đặt phòng, confirm, check-in/out, dịch vụ, hóa đơn |
| Booking Services | `/api/booking-services/` | 2 | Cập nhật / xoá dịch vụ trong booking |
| Invoices | `/api/invoices/` | 7 | CRUD + thanh toán |
| Reports | `/api/reports/` | 4 | Doanh thu, trạng thái phòng, thống kê booking, top dịch vụ |
| Pricing | `/api/pricing/` | 1 | Tính giá booking dự kiến (module riêng) |

> Danh sách chi tiết: [`docs/Nhom04_Danh_sach_API.md`](docs/Nhom04_Danh_sach_API.md)

---

## 7. Điểm Nổi Bật

- **Phân quyền rõ ràng**: `quan_ly` và `le_tan` có quyền khác nhau; mọi endpoint đều yêu cầu xác thực, không để truy cập tự do.
- **Soft delete**: Dữ liệu quan trọng (phòng, khách hàng, hóa đơn…) được đánh dấu `is_deleted` thay vì xoá cứng, giữ nguyên lịch sử hệ thống.
- **Kiểm tra trùng lịch**: Serializer BookingCreate kiểm tra phòng không bị đặt trùng khoảng thời gian.
- **Mã hoá mật khẩu**: Django password hasher, không lưu plain text.
- **Module Pricing độc lập**: `hotel_app` gọi sang module `pricing` để tính giá, tách biệt logic định giá khỏi nghiệp vụ booking.
- **Hóa đơn tự động cập nhật**: Mỗi lần thêm/sửa/xoá dịch vụ hoặc check-out, `InvoiceService` tính lại `room_charge + service_charge = total`.
- **Filter / Search / Ordering**: Hầu hết endpoint list hỗ trợ lọc, tìm kiếm và sắp xếp qua query parameter.

---

## 8. Cài Đặt Và Chạy Dự Án

**Cài thư viện:**

```bash
pip install -r requirements.txt
```

**Tạo database MySQL và chạy migration:**

```bash
# Tạo database (nếu chưa có)
mysql -u root -p -e "CREATE DATABASE hotel_management CHARACTER SET utf8mb4;"

# Cấu hình kết nối trong config/settings.py (USER, PASSWORD, HOST, PORT)

# Chạy migration
python manage.py migrate
```

**Import dữ liệu mẫu (tuỳ chọn):**

```bash
mysql -u root -p hotel_management < scripts/script_create_db_hotel_management.sql
mysql -u root -p hotel_management < scripts/script_insert_data_hotel_management.sql
```

**Chạy server:**

```bash
python manage.py runserver 127.0.0.1:8000
```

Base URL: `http://127.0.0.1:8000/api/`

---

## 9. Kiểm Thử

### Unit test

```bash
python manage.py test
```

Kết quả:

```text
Ran 140 tests — OK
```

Bao gồm: kiểm thử model, service, serializer, view/API, phân quyền, soft delete và các luồng lỗi quan trọng.

### E2E script trên database thật

```bash
# Full API (77 endpoint, bao gồm CHECK data và kiểm tra permission)
python hotel_app/tests/e2e/full_api/test_e2e_api.py --prefix demo01

# Booking flow (luồng lễ tân: đặt phòng → check-in → dịch vụ → thanh toán)
python hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py --prefix book01
```

Sau khi chạy, báo cáo HTML được tạo tại:

```text
hotel_app/tests/e2e/full_api/bao_cao_e2e_api.html
hotel_app/tests/e2e/booking_flow/bao_cao_e2e_booking_flow.html
```

E2E script kiểm tra:
- HTTP status code đúng với expected.
- Giá trị field trong response body (username, role, price, status…).
- Tính toán hóa đơn chính xác (`room_charge`, `service_charge`, `total`).
- Chuyển trạng thái booking và phòng đúng quy trình.
- Phân quyền: `le_tan` nhận 403 khi gọi endpoint chỉ dành cho `quan_ly`.
- Filter/search trả về đúng dữ liệu theo tiêu chí.
- DB verification sau khi gọi API.

### Postman

Import collection và chạy demo trực tiếp:

```text
hotel_app/tests/postman/hotel_management_postman_collection.json
```

Collection gồm 2 kịch bản:
- **Kịch bản 1**: Luồng lễ tân — tạo khách hàng, đặt phòng, check-in, dịch vụ, check-out, thanh toán.
- **Kịch bản 2**: Luồng quản lý — thêm loại phòng, phòng, dịch vụ, xác nhận đặt phòng, xem báo cáo.

---

## 10. Tài Liệu Liên Quan

| Tài liệu | Đường dẫn |
|---|---|
| Danh sách 77 endpoint chi tiết | [`docs/Nhom04_Danh_sach_API.md`](docs/Nhom04_Danh_sach_API.md) |
| Kịch bản demo API | [`docs/kich_ban_demo.md`](docs/kich_ban_demo.md) |
| Giải thích module Pricing | [`docs/Nhom04_Giai_thich_app_pricing.md`](docs/Nhom04_Giai_thich_app_pricing.md) |
| Postman collection | [`hotel_app/tests/postman/hotel_management_postman_collection.json`](hotel_app/tests/postman/hotel_management_postman_collection.json) |
| Script tạo bảng | [`scripts/script_create_db_hotel_management.sql`](scripts/script_create_db_hotel_management.sql) |
| Script dữ liệu mẫu | [`scripts/script_insert_data_hotel_management.sql`](scripts/script_insert_data_hotel_management.sql) |
| E2E full API script | [`hotel_app/tests/e2e/full_api/test_e2e_api.py`](hotel_app/tests/e2e/full_api/test_e2e_api.py) |
| E2E booking flow script | [`hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py`](hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py) |
