# Danh sách API Endpoint — Hệ thống Quản lý Khách sạn
**Nhóm 04 | Môn: Lập trình Python**

> Tổng cộng: **77 endpoint** | Base URL: `http://127.0.0.1:8000`

---

## 1. Auth — Xác thực (6 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| POST | `/api/auth/register/` | Đăng ký tài khoản | Công khai |
| POST | `/api/auth/login/` | Đăng nhập | Công khai |
| POST | `/api/auth/logout/` | Đăng xuất | Đã đăng nhập |
| GET | `/api/auth/profile/` | Xem hồ sơ cá nhân | Đã đăng nhập |
| PUT | `/api/auth/profile/` | Cập nhật hồ sơ | Đã đăng nhập |
| PUT | `/api/auth/change-password/` | Đổi mật khẩu | Đã đăng nhập |

---

## 2. Users — Tài khoản (8 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/users/` | Danh sách tài khoản | Đã đăng nhập |
| POST | `/api/users/` | Tạo tài khoản mới | Quản lý |
| GET | `/api/users/{id}/` | Chi tiết tài khoản | Đã đăng nhập |
| PUT | `/api/users/{id}/` | Cập nhật tài khoản | Quản lý |
| PATCH | `/api/users/{id}/` | Cập nhật một phần | Quản lý |
| DELETE | `/api/users/{id}/` | Vô hiệu hoá tài khoản | Quản lý |
| POST | `/api/users/{id}/disable/` | Khoá tài khoản | Quản lý |
| POST | `/api/users/{id}/enable/` | Mở khoá tài khoản | Quản lý |

---

## 3. Departments — Phòng ban (6 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/departments/` | Danh sách phòng ban | Đã đăng nhập |
| POST | `/api/departments/` | Tạo phòng ban | Quản lý |
| GET | `/api/departments/{id}/` | Chi tiết phòng ban | Đã đăng nhập |
| PUT | `/api/departments/{id}/` | Cập nhật phòng ban | Quản lý |
| PATCH | `/api/departments/{id}/` | Cập nhật một phần | Quản lý |
| DELETE | `/api/departments/{id}/` | Xoá mềm phòng ban | Quản lý |

---

## 4. Employees — Nhân viên (6 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/employees/` | Danh sách nhân viên | Đã đăng nhập |
| POST | `/api/employees/` | Tạo nhân viên mới | Quản lý |
| GET | `/api/employees/{id}/` | Chi tiết nhân viên | Đã đăng nhập |
| PUT | `/api/employees/{id}/` | Cập nhật nhân viên | Quản lý |
| PATCH | `/api/employees/{id}/` | Cập nhật một phần | Quản lý |
| DELETE | `/api/employees/{id}/` | Vô hiệu hoá nhân viên | Quản lý |

---

## 5. Customers — Khách hàng (6 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/customers/` | Danh sách khách hàng | Đã đăng nhập |
| POST | `/api/customers/` | Tạo khách hàng | Đã đăng nhập |
| GET | `/api/customers/{id}/` | Chi tiết khách hàng | Đã đăng nhập |
| PUT | `/api/customers/{id}/` | Cập nhật khách hàng | Đã đăng nhập |
| PATCH | `/api/customers/{id}/` | Cập nhật một phần | Đã đăng nhập |
| DELETE | `/api/customers/{id}/` | Xoá mềm khách hàng | Quản lý |

---

## 6. Room Types — Loại phòng (6 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/room-types/` | Danh sách loại phòng | Đã đăng nhập |
| POST | `/api/room-types/` | Tạo loại phòng | Quản lý |
| GET | `/api/room-types/{id}/` | Chi tiết loại phòng | Đã đăng nhập |
| PUT | `/api/room-types/{id}/` | Cập nhật loại phòng | Quản lý |
| PATCH | `/api/room-types/{id}/` | Cập nhật một phần | Quản lý |
| DELETE | `/api/room-types/{id}/` | Xoá mềm loại phòng | Quản lý |

---

## 7. Rooms — Phòng (7 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/rooms/` | Danh sách phòng | Đã đăng nhập |
| POST | `/api/rooms/` | Tạo phòng mới | Quản lý |
| GET | `/api/rooms/{id}/` | Chi tiết phòng | Đã đăng nhập |
| PUT | `/api/rooms/{id}/` | Cập nhật phòng | Quản lý |
| PATCH | `/api/rooms/{id}/` | Cập nhật một phần | Quản lý |
| DELETE | `/api/rooms/{id}/` | Xoá mềm phòng | Quản lý |
| PUT | `/api/rooms/{id}/status/` | Đổi trạng thái phòng | Quản lý |

---

## 8. Services — Dịch vụ (6 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/services/` | Danh sách dịch vụ (active) | Đã đăng nhập |
| POST | `/api/services/` | Tạo dịch vụ | Quản lý |
| GET | `/api/services/{id}/` | Chi tiết dịch vụ | Đã đăng nhập |
| PUT | `/api/services/{id}/` | Cập nhật dịch vụ | Quản lý |
| PATCH | `/api/services/{id}/` | Cập nhật một phần | Quản lý |
| DELETE | `/api/services/{id}/` | Vô hiệu hoá dịch vụ | Quản lý |

---

## 9. Bookings — Đặt phòng (12 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/bookings/` | Danh sách đặt phòng | Đã đăng nhập |
| POST | `/api/bookings/` | Tạo đặt phòng + hoá đơn | Đã đăng nhập |
| GET | `/api/bookings/{id}/` | Chi tiết đặt phòng | Đã đăng nhập |
| PUT | `/api/bookings/{id}/` | Cập nhật ghi chú | Đã đăng nhập |
| DELETE | `/api/bookings/{id}/` | Huỷ đặt phòng | Đã đăng nhập |
| PUT | `/api/bookings/{id}/confirm/` | Xác nhận đặt phòng | Đã đăng nhập |
| PUT | `/api/bookings/{id}/cancel/` | Huỷ đặt phòng (action) | Đã đăng nhập |
| PUT | `/api/bookings/{id}/check-in/` | Check-in | Đã đăng nhập |
| PUT | `/api/bookings/{id}/check-out/` | Check-out + cập nhật hoá đơn | Đã đăng nhập |
| GET | `/api/bookings/{id}/invoice/` | Xem hoá đơn theo booking | Đã đăng nhập |
| GET | `/api/bookings/{id}/services/` | Danh sách dịch vụ đã dùng | Đã đăng nhập |
| POST | `/api/bookings/{id}/services/` | Thêm dịch vụ vào booking | Đã đăng nhập |

---

## 10. Booking Services — Dịch vụ theo booking (2 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| PUT | `/api/booking-services/{id}/` | Cập nhật số lượng dịch vụ | Đã đăng nhập |
| DELETE | `/api/booking-services/{id}/` | Xoá dịch vụ khỏi booking | Đã đăng nhập |

---

## 11. Invoices — Hoá đơn (7 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/invoices/` | Danh sách hoá đơn | Đã đăng nhập |
| POST | `/api/invoices/` | Lập hoá đơn thủ công | Đã đăng nhập |
| GET | `/api/invoices/{id}/` | Chi tiết hoá đơn | Đã đăng nhập |
| PUT | `/api/invoices/{id}/` | Cập nhật hoá đơn | Đã đăng nhập |
| PATCH | `/api/invoices/{id}/` | Cập nhật một phần | Đã đăng nhập |
| DELETE | `/api/invoices/{id}/` | Xoá mềm hoá đơn | Đã đăng nhập |
| PUT | `/api/invoices/{id}/pay/` | Thanh toán hoá đơn | Đã đăng nhập |

---

## 12. Reports — Báo cáo (4 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| GET | `/api/reports/revenue/` | Báo cáo doanh thu | Quản lý |
| GET | `/api/reports/room-status/` | Thống kê trạng thái phòng | Quản lý |
| GET | `/api/reports/booking-statistics/` | Thống kê đặt phòng | Quản lý |
| GET | `/api/reports/top-services/?top=N` | Top N dịch vụ sử dụng nhiều nhất | Quản lý |

---

## 13. Pricing — Tính giá (1 endpoint)

| Method | URL | Mô tả | Quyền |
|--------|-----|--------|-------|
| POST | `/api/pricing/calculate-booking-price/` | Tính giá đặt phòng (có áp dụng giảm giá VIP) | Đã đăng nhập |

---

## Tổng kết

| Nhóm | Số endpoint |
|------|-------------|
| Auth | 6 |
| Users | 8 |
| Departments | 6 |
| Employees | 6 |
| Customers | 6 |
| Room Types | 6 |
| Rooms | 7 |
| Services | 6 |
| Bookings | 12 |
| Booking Services | 2 |
| Invoices | 7 |
| Reports | 4 |
| Pricing | 1 |
| **Tổng** | **77** |

---

## Query parameters hỗ trợ

| Endpoint | Filter | Search | Ordering |
|----------|--------|--------|----------|
| `/api/users/` | `role`, `is_active` | `username`, `email` | `created_at`, `username` |
| `/api/employees/` | `department`, `status`, `shift` | `full_name`, `phone` | `created_at`, `full_name` |
| `/api/customers/` | `customer_type`, `phone`, `id_card` | `full_name`, `phone`, `email` | `created_at`, `full_name` |
| `/api/rooms/` | `status`, `room_type`, `floor`, `capacity`, `room_type_id` | `room_number` | `floor`, `room_number` |
| `/api/room-types/` | `name` | `name`, `description` | `name`, `price_per_night`, `capacity` |
| `/api/services/` | `is_active` | `name` | `name`, `price` |
| `/api/bookings/` | `status`, `customer`, `room`, `customer_id`, `room_id`, `tu_ngay`, `den_ngay` | — | `created_at`, `check_in`, `check_out` |
| `/api/invoices/` | `payment_status`, `payment_method` | — | `created_at`, `total`, `paid_at` |
| `/api/reports/revenue/` | `tu_ngay`, `den_ngay` | — | — |
| `/api/reports/booking-statistics/` | `tu_ngay`, `den_ngay` | — | — |
| `/api/reports/top-services/` | `top` (số nguyên) | — | — |
