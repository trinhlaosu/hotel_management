# Kịch Bản Demo Hệ Thống Quản Lý Khách Sạn

Tài liệu này mô tả kịch bản thao tác chi tiết dùng để demo tính năng hoặc quay video báo cáo. Kịch bản được chia làm 2 luồng chính: Luồng dành cho Lễ tân (User) và Luồng dành cho Quản lý (Admin). 
Bạn có thể sử dụng file `hotel_management_postman_collection.json` (trong thư mục `hotel_app/tests/postman`) đã được thiết lập sẵn theo đúng thứ tự các bước dưới đây để test.

---

## Kịch Bản 1: Luồng Nghiệp Vụ Nhân Viên (User / Lễ Tân)
*Luồng này thể hiện toàn bộ vòng đời của một quy trình phục vụ khách hàng: từ lúc tới hỏi phòng, báo giá, đặt phòng, sử dụng dịch vụ cho đến khi check-out và thanh toán.*
`
| STT | Tên Bước | Method | URL | Mô tả thao tác |
|:---:|---|:---:|---|---|
| 1 | **Auth - Login (Lễ Tân)** | `POST` | `/api/auth/login/` | Đăng nhập tài khoản lễ tân để lấy Token xác thực |
| 2 | **Auth - Profile** | `GET` | `/api/auth/profile/` | Kiểm tra thông tin cá nhân của nhân viên đang thao tác |
| 3 | **Customers - List** | `GET` | `/api/customers/` | Tìm kiếm xem khách hàng đã tồn tại trong hệ thống chưa |
| 4 | **Customers - Create** | `POST` | `/api/customers/` | Khởi tạo thông tin khách hàng mới |
| 5 | **Room Types - List** | `GET` | `/api/room-types/` | Xem các loại phòng hiện có của khách sạn |
| 6 | **Rooms - Available** | `GET` | `/api/rooms/?status=trong` | Tìm kiếm các phòng đang trống để tư vấn cho khách |
| 7 | **Pricing - Calculate Price**| `POST` | `/api/pricing/calculate-booking-price/`| Tính toán tổng số tiền phòng dự kiến dựa trên số ngày lưu trú |
| 8 | **Bookings - Create** | `POST` | `/api/bookings/` | Tạo mã Đặt phòng (Booking) cho khách hàng |
| 9 | **Bookings - Detail** | `GET` | `/api/bookings/<id>/` | Xem chi tiết thông tin Booking vừa tạo |
| 10 | **Bookings - Confirm** | `PUT` | `/api/bookings/<id>/confirm/` | Xác nhận đơn đặt phòng |
| 11 | **Bookings - Check-in** | `PUT` | `/api/bookings/<id>/check-in/` | Check-in cho khách khi khách đến nhận phòng |
| 12 | **Booking Services - Add**| `POST` | `/api/bookings/<id>/services/`| Thêm dịch vụ phát sinh (vd: Ăn sáng, Giặt ủi) vào booking |
| 13 | **Booking Services - List**| `GET` | `/api/bookings/<id>/services/`| Kiểm tra lại danh sách dịch vụ khách đã sử dụng |
| 14 | **Bookings - Check-out** | `PUT` | `/api/bookings/<id>/check-out/` | Khách trả phòng (Check-out) |
| 15 | **Invoices - View** | `GET` | `/api/bookings/<id>/invoice/` | Xuất hóa đơn tổng (tiền phòng + dịch vụ) |
| 16 | **Invoices - Pay** | `PUT` | `/api/invoices/<id>/pay/` | Nhận tiền khách thanh toán và cập nhật trạng thái hóa đơn |
| 17 | **Auth - Logout** | `POST` | `/api/auth/logout/` | Đăng xuất khỏi phiên làm việc |

---

## Kịch Bản 2: Luồng Quản Trị Hệ Thống (Admin)
*Luồng này thể hiện các quyền hạn đặc thù của người Quản trị: Thiết lập danh mục (thêm loại phòng, thêm phòng, thêm dịch vụ), duyệt đặt phòng và theo dõi báo cáo thống kê chuyên sâu.*

| STT | Tên Bước | Method | URL | Mô tả thao tác |
|:---:|---|:---:|---|---|
| 1 | **Đăng nhập** | `POST` | `/api/auth/login/` | Đăng nhập tài khoản Quản lý (`ql001`) |
| 2 | **Thêm loại phòng mới** | `POST` | `/api/room-types/` | Định nghĩa loại phòng mới (Vd: Deluxe, 800.000 VND/đêm) |
| 3 | **Thêm phòng mới** | `POST` | `/api/rooms/` | Thêm phòng vật lý mới (Vd: phòng 101, tầng 1, loại Deluxe) |
| 4 | **Thêm dịch vụ** | `POST` | `/api/services/` | Thêm dịch vụ mới cho khách sạn (Vd: Breakfast, 50.000 VND) |
| 5 | **Xác nhận đặt phòng** | `PUT` | `/api/bookings/<id>/confirm/` | Admin phê duyệt đơn đặt phòng do lễ tân tạo |
| 6 | **Xem thống kê doanh thu** | `GET` | `/api/reports/revenue/` | Lấy dữ liệu báo cáo thống kê doanh thu |
| 7 | **Xem top dịch vụ** | `GET` | `/api/reports/top-services/` | Lấy dữ liệu thống kê top dịch vụ được sử dụng nhiều nhất |
| 8 | **Đăng xuất** | `POST` | `/api/auth/logout/` | Đăng xuất khỏi hệ thống |

---
**Hướng dẫn sử dụng chung:**
- Mở **Postman**, chọn `Import` -> kéo thả file `hotel_app/tests/postman/hotel_management_postman_collection.json` vào.
- Khi quay video demo, bạn chỉ việc bấm chạy tuần tự từ trên xuống dưới theo các bước trong Collection đã được chuẩn bị sẵn, kết hợp với lời dẫn kịch bản tương ứng để đảm bảo tính trơn tru, logic.
