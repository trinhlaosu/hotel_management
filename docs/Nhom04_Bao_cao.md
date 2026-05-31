# ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH
## TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN

&nbsp;

&nbsp;

# XÂY DỰNG RESTFUL API QUẢN LÝ KHÁCH SẠN SỬ DỤNG DJANGO VÀ MYSQL

&nbsp;

**Nhóm 04**

**Sinh viên thực hiện:**

| STT | Họ tên | MSSV | Ngành |
|:---:|---|---|---|
| 1 | Trịnh Thị Mỹ Chi | 25410022 | CNTT |
| 2 | Võ Mộng Chuyền | 25410024 | CNTT |
| 3 | Lê Đức Minh | 25410092 | CNTT |

&nbsp;

**TP. HỒ CHÍ MINH – 06/2026**

---

## GIỚI THIỆU

Đề tài xây dựng hệ thống RESTful API quản lý nội bộ khách sạn, phục vụ hai vai trò chính là quản lý và lễ tân. Hệ thống được phát triển bằng ngôn ngữ Python với framework Django REST Framework, tổ chức theo mô hình MVT kết hợp service layer và sử dụng MySQL để lưu trữ dữ liệu. Django REST Framework hỗ trợ triển khai API thông qua Serializer, ViewSet, Router, cơ chế phân quyền theo phiên làm việc và phản hồi dữ liệu chuẩn JSON. Kết quả đạt được là Backend API Server hoàn chỉnh với 10 bảng cơ sở dữ liệu, 9 nhóm chức năng lớn, 39 endpoint chính, khoảng 77 thao tác API, kèm dữ liệu mẫu, Postman Collection và 136 test tự động.

Nhóm tự phân tích yêu cầu, thiết kế cơ sở dữ liệu và triển khai hệ thống theo phạm vi đồ án môn học, không sử dụng mã nguồn mẫu từ bên ngoài. Trong quá trình thực hiện, nhóm tham khảo tài liệu chính thức của Django [1], Django REST Framework [2], MySQL [3], giao thức HTTP/REST [4] và Postman [5]. Nhóm có sử dụng công cụ AI (Claude [6], ChatGPT [7]) để hỗ trợ rà soát mã nguồn, xây dựng kịch bản kiểm thử và hoàn thiện báo cáo.

---

## MÔ TẢ CƠ SỞ DỮ LIỆU

### Tổng quan cơ sở dữ liệu

Hệ thống sử dụng MySQL với tên cơ sở dữ liệu `hotel_management`, gồm 10 bảng phục vụ các nghiệp vụ quản lý khách sạn, được trình bày chi tiết trong sơ đồ ERD [Hình 1].

&nbsp;

**Hình 1. Sơ đồ ERD cơ sở dữ liệu quản lý khách sạn**

&nbsp;

Hình 1 thể hiện 10 bảng chính và các mối quan hệ. Bảng Booking đóng vai trò trung tâm, liên kết với Customer, Room, Employee, đồng thời phát sinh Invoice và BookingService.

### Danh sách bảng và ràng buộc dữ liệu

Hệ thống gồm 10 bảng chính, được mô tả trong Bảng 1.

**Bảng 1. Mô tả các bảng cơ sở dữ liệu**

| STT | Tên bảng | Mô tả | Trường chính |
|:---:|---|---|---|
| 1 | User | Lưu tài khoản đăng nhập nội bộ | username, password, email, role |
| 2 | Department | Lưu thông tin phòng ban | name, description |
| 3 | Employee | Lưu thông tin nhân viên | user, full_name, department, salary, shift, status |
| 4 | Customer | Lưu thông tin khách hàng | full_name, phone, id_card, customer_type |
| 5 | RoomType | Lưu thông tin loại phòng | name, price_per_night, capacity, description |
| 6 | Room | Lưu thông tin phòng và trạng thái phòng | room_number, floor, status |
| 7 | Booking | Lưu thông tin đặt phòng | check_in, check_out, status, note |
| 8 | Invoice | Lưu hóa đơn và trạng thái thanh toán | room_charge, service_charge, total, payment_status |
| 9 | Service | Lưu danh sách dịch vụ khách sạn | name, price, is_active |
| 10 | BookingService | Lưu dịch vụ khách sử dụng trong từng đặt phòng | booking, service, quantity, subtotal |

Các quan hệ chính: User - Employee (1-1), Department - Employee (1-N), RoomType - Room (1-N), Customer - Booking (1-N), Room - Booking (1-N), Employee - Booking (1-N), Booking - Invoice (1-1), Booking - BookingService (1-N), Service - BookingService (1-N).

Một số ràng buộc nghiệp vụ được áp dụng trong mã nguồn: số điện thoại và CCCD khách hàng là duy nhất; số phòng là duy nhất; khi hủy hoặc check-out, trạng thái phòng tự cập nhật về trống; BookingService.subtotal được tính theo đơn giá dịch vụ và số lượng; hóa đơn được cập nhật khi check-out theo tiền phòng và tiền dịch vụ thực tế.

---

## THIẾT KẾ HỆ THỐNG

### Kiến trúc hệ thống theo mô hình MVT

Hệ thống tổ chức theo mô hình Django MVT kết hợp Django REST Framework và service layer. Django REST Framework hỗ trợ xây dựng API thông qua Router, ViewSet, Serializer, cơ chế phân quyền và phản hồi JSON. Service layer được tách riêng để xử lý nghiệp vụ như đặt phòng, tính giá, lập hóa đơn và thống kê, không để logic này lẫn vào View. Sơ đồ dưới đây mô tả kiến trúc xử lý của hệ thống [Hình 2].

&nbsp;

**Hình 2. Kiến trúc hệ thống Web API quản lý khách sạn**

&nbsp;

Hình 2 cho thấy luồng xử lý từ trên xuống: Client/Postman gửi HTTP request → URL Router định tuyến đến ViewSet phù hợp → Serializer validate và chuyển đổi dữ liệu JSON → Service Layer xử lý nghiệp vụ → Model tương tác với MySQL qua ORM → trả kết quả JSON về client.

### Phân quyền người dùng

Hệ thống áp dụng xác thực phiên làm việc (session-based authentication) và chia người dùng thành ba nhóm [Bảng 2].

**Bảng 2. Phân quyền theo vai trò người dùng**

| Đối tượng người dùng | Quyền sử dụng |
|---|---|
| Guest / Chưa đăng nhập | Đăng ký và đăng nhập. Tài khoản mới chưa kích hoạt, cần Quản lý duyệt. |
| Quản lý | Toàn quyền: tài khoản, nhân viên, phòng ban, loại phòng, dịch vụ, hóa đơn, báo cáo. |
| Lễ tân/Nhân viên | Khách hàng, phòng, đặt phòng, check-in, check-out, dịch vụ, hóa đơn, thanh toán. |

Phân quyền được triển khai qua hai lớp: `SessionAuthenticated` kiểm tra người dùng đã đăng nhập, `ManagerOnly` kiểm tra quyền quản lý. Tài khoản mới tạo mặc định role lễ tân và chưa kích hoạt, cần Quản lý duyệt.

### Sơ đồ chức năng hệ thống

Hệ thống được chia thành 9 nhóm chức năng chính, triển khai thành 39 endpoint và khoảng 77 thao tác API. Sơ đồ chức năng dưới đây trình bày tổng quan toàn bộ hệ thống [Hình 3].

&nbsp;

**Hình 3. Sơ đồ chức năng hệ thống quản lý khách sạn**

&nbsp;

Hình 3 thể hiện 9 nhóm chức năng: xác thực, quản lý tài khoản, khách hàng, nhân viên, phòng, đặt phòng, dịch vụ, hóa đơn và báo cáo - thống kê. Các nhóm được triển khai thành 39 endpoint chính và khoảng 77 thao tác API, trong đó đặt phòng và thanh toán là chức năng trọng tâm.

### Chức năng trọng tâm: Đặt phòng và thanh toán

Chức năng đặt phòng và thanh toán là nghiệp vụ cốt lõi, liên kết nhiều bảng nhất: Customer, Room, RoomType, Booking, Service, BookingService, Invoice. Sơ đồ lớp dưới đây mô tả thiết kế chi tiết [Hình 4].

&nbsp;

**Hình 4. Sơ đồ lớp chức năng quản lý đặt phòng và thanh toán**

&nbsp;

Hình 4 cho thấy Booking là lớp trung tâm liên kết tất cả các thực thể. Khi tạo đặt phòng, hệ thống tự động gọi module pricing để tính giá và lập hóa đơn sơ bộ. Khi check-out, hóa đơn được cập nhật theo dịch vụ thực tế sử dụng trong kỳ lưu trú.

Module pricing (`BookingPriceCalculator`) được tách thành app riêng, áp dụng công thức tính giá như sau:

```
base_price   = price_per_night × số_đêm
weekend_fee  = price_per_night × 10% × số_đêm_cuối_tuần
vip_discount = (base_price + weekend_fee) × 10%
final_price  = base_price + weekend_fee − vip_discount
```

Sơ đồ luồng nội bộ của module pricing được trình bày trong Hình 5.

&nbsp;

**Hình 5. Luồng chức năng đặt phòng và thanh toán**

&nbsp;

Hình 5 mô tả luồng tính giá gồm 6 bước: nhận input (room, check_in/check_out, customer_type) → tính số đêm → tính base_price → đếm đêm cuối tuần → tính weekend_fee → rẽ nhánh VIP/regular → trả về final_price. Module này đảm bảo giá luôn nhất quán dù được gọi từ API tạo đặt phòng hay check-out.

Luồng xử lý 12 bước của toàn bộ chức năng đặt phòng và thanh toán được trình bày trong Hình 6.

&nbsp;

**Hình 6. Luồng chức năng đặt phòng và thanh toán (12 bước)**

&nbsp;

Hình 6 mô tả toàn bộ quy trình: lễ tân tìm phòng trống → ước tính giá → tạo đặt phòng → quản lý xác nhận → check-in → ghi nhận dịch vụ → check-out → xem hóa đơn → thanh toán → báo cáo. Đây là chức năng thể hiện rõ nhất sự phối hợp xuyên suốt giữa các API, module pricing và cơ sở dữ liệu.

Ngoài ra, module pricing còn được gọi qua API `POST /api/pricing/calculate-booking-price/` để lễ tân ước tính chi phí trước khi tạo đặt phòng, giúp tránh nhầm lẫn về giá.

---

## TRIỂN KHAI VÀ KIỂM THỬ API

### 4.1. Kiến trúc triển khai

Hệ thống được triển khai và kiểm thử trên môi trường cục bộ với Django Development Server. Kiến trúc triển khai gồm ba thành phần chính được trình bày trong Hình 7.

&nbsp;

**Hình 7. Kiến trúc triển khai hệ thống Web API quản lý khách sạn**

&nbsp;

Hình 7 cho thấy Postman/Client gửi HTTP request đến Django Web API Server qua các endpoint đã định nghĩa. Django tiếp nhận, xử lý nghiệp vụ qua Service Layer, truy xuất MySQL qua ORM và trả kết quả JSON về client.

### 4.2. Kịch bản kiểm thử

Nhóm kiểm thử theo hai luồng vai trò chạy nối tiếp nhau qua Postman: Quản lý thiết lập danh mục và xác nhận đặt phòng; Lễ tân tiếp nhận và xử lý toàn bộ quy trình lưu trú.

**Kịch bản kiểm thử 1. Luồng Quản lý (tài khoản ql001)**

**Bảng 4. Kịch bản kiểm thử luồng Quản lý**

| STT | Method | API | Chức năng |
|:---:|---|---|---|
| 1 | POST | `/api/auth/login/` | Đăng nhập |
| 2 | POST | `/api/room-types/` | Thêm loại phòng mới (Deluxe, 800.000 VND/đêm) |
| 3 | POST | `/api/rooms/` | Thêm phòng mới (phòng 101, tầng 1, loại Deluxe) |
| 4 | POST | `/api/services/` | Thêm dịch vụ (Breakfast, 50.000 VND) |
| 5 | PUT | `/api/bookings/<id>/confirm/` | Xác nhận đặt phòng do lễ tân tạo |
| 6 | GET | `/api/reports/revenue/` | Xem thống kê doanh thu |
| 7 | GET | `/api/reports/top-services/` | Xem top dịch vụ được sử dụng nhiều |
| 8 | POST | `/api/auth/logout/` | Đăng xuất |

Luồng Quản lý kiểm tra các quyền hạn đặc thù: thêm danh mục phòng và dịch vụ, duyệt đặt phòng và xem báo cáo thống kê.

**Kịch bản kiểm thử 2. Luồng Lễ tân (tài khoản lt001)**

**Bảng 5. Kịch bản kiểm thử luồng Lễ tân**

| STT | Method | API | Chức năng |
|:---:|---|---|---|
| 1 | POST | `/api/auth/login/` | Đăng nhập tài khoản lễ tân |
| 2 | POST | `/api/customers/` | Thêm khách hàng mới |
| 3 | GET | `/api/rooms/?status=trong` | Tìm phòng trống |
| 4 | POST | `/api/pricing/calculate-booking-price/` | Ước tính giá phòng trước khi đặt |
| 5 | POST | `/api/bookings/` | Tạo đặt phòng và tự động lập hóa đơn |
| 6 | PUT | `/api/bookings/<id>/check-in/` | Check-in (sau khi quản lý xác nhận) |
| 7 | POST | `/api/bookings/<id>/services/` | Ghi nhận dịch vụ khách sử dụng |
| 8 | PUT | `/api/bookings/<id>/check-out/` | Check-out và cập nhật hóa đơn |
| 9 | GET | `/api/bookings/<id>/invoice/` | Xem hóa đơn tổng kết |
| 10 | PUT | `/api/invoices/<id>/pay/` | Thanh toán hóa đơn |
| 11 | POST | `/api/auth/logout/` | Đăng xuất |

Hai luồng thể hiện rõ sự phân quyền giữa các vai trò và sự liên kết giữa Customer, Room, Booking, BookingService, Service và Invoice. Kết quả được minh chứng qua hình chụp Postman trong phần phụ lục hình.

Ngoài Postman, nhóm thực hiện Django Unit/API Test và E2E script trên database thật với tổng cộng 136 test tự động, phân thành các nhóm: model, service, API, phân quyền, validate dữ liệu và luồng nghiệp vụ chính (booking flow). File kiểm thử được tổ chức trong thư mục `hotel_app/tests/`.

---

## KẾT LUẬN

Trong quá trình thực hiện đồ án, nhóm đã phân tích yêu cầu, thiết kế cơ sở dữ liệu, xây dựng Web API và kiểm thử các chức năng chính. Hệ thống được phát triển bằng Python, Django REST Framework và MySQL, tổ chức theo kiến trúc MVT kết hợp service layer, phục vụ các nghiệp vụ quản lý nội bộ khách sạn gồm tài khoản, nhân viên, khách hàng, phòng, đặt phòng, dịch vụ, hóa đơn và thống kê.

Kết quả đạt được là Backend API Server hoàn chỉnh với 10 bảng cơ sở dữ liệu, 39 endpoint chính, khoảng 77 thao tác API, kèm dữ liệu mẫu, Postman Collection và 136 test tự động. Nhóm đánh giá cao nhất là luồng tạo đặt phòng và check-out vì đây là luồng xử lý chính của hệ thống, nơi hai API quan trọng tự động gọi module tính giá phòng để tính chi phí theo số đêm, phụ thu cuối tuần và chiết khấu VIP, sau đó lập hoặc cập nhật hóa đơn, thể hiện rõ sự phối hợp xuyên suốt từ View/ViewSet qua Service, Model đến Invoice.

Hạn chế hiện tại là hệ thống mới tập trung vào Backend API, chưa có giao diện người dùng hoàn chỉnh, mới kiểm thử trên môi trường cục bộ và một số chức năng như thống kê, phân quyền chi tiết vẫn còn ở mức cơ bản.

---

## TÀI LIỆU THAM KHẢO

[1] Django Software Foundation, Django Documentation. Link: https://docs.djangoproject.com/ (Ngày truy cập: 30/05/2026).

[2] Django REST Framework, Django REST Framework Documentation. Link: https://www.django-rest-framework.org/ (Ngày truy cập: 30/05/2026).

[3] Oracle Corporation, MySQL 8.0 Reference Manual. Link: https://dev.mysql.com/doc/refman/8.0/en/ (Ngày truy cập: 30/05/2026).

[4] Mozilla Developer Network, HTTP request methods. Link: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods (Ngày truy cập: 30/05/2026).

[5] Postman, Postman Learning Center. Link: https://learning.postman.com/ (Ngày truy cập: 30/05/2026).

[6] Anthropic, Claude AI. Link: https://claude.ai/ (Ngày truy cập: 30/05/2026).

[7] OpenAI, ChatGPT. Link: https://chat.openai.com/ (Ngày truy cập: 30/05/2026).

---

## PHỤ LỤC PHÂN CÔNG NHIỆM VỤ

| STT | Thành viên | Nhiệm vụ |
|:---:|---|---|
| 1 | Trịnh Thị Mỹ Chi | Nhóm trưởng: điều phối nhóm, phân chia và theo dõi tiến độ. Tham gia phân tích đề tài, xác định phạm vi chức năng, liệt kê danh sách API và phân quyền người dùng. Khởi tạo source code, cấu hình project Django, kết nối MySQL, xây dựng các API tài khoản, nhân viên, phòng ban và phân quyền. Tổng hợp, chỉnh sửa và kiểm tra báo cáo trước khi nộp. Tham gia thuyết trình. |
| 2 | Võ Mộng Chuyền | Tham gia phân tích đề tài. Thiết kế cơ sở dữ liệu, xây dựng danh sách bảng, khóa chính, khóa ngoại và dữ liệu mẫu. Thiết kế sơ đồ ERD và sơ đồ chức năng hệ thống. Xây dựng các API khách hàng, loại phòng, phòng và tìm kiếm phòng trống. Hỗ trợ chuẩn bị slide thuyết trình. Tham gia thuyết trình. |
| 3 | Lê Đức Minh | Tham gia phân tích đề tài. Thiết kế sơ đồ lớp chức năng, sơ đồ kiến trúc hệ thống và sơ đồ kiến trúc triển khai. Xây dựng các API đặt phòng, dịch vụ, hóa đơn, thanh toán và thống kê. Kiểm thử các API bằng Postman, chụp hình minh chứng. Chuẩn bị nội dung demo, quay video và hoàn thiện phụ lục hình. Tham gia thuyết trình. |

---

## PHỤ LỤC TÓM TẮT KẾT QUẢ

| STT | Nội dung | Kết quả |
|:---:|---|---|
| 1 | Chủ đề | Xây dựng RESTful API quản lý khách sạn bằng Python, Django và MySQL |
| 2 | Giải pháp lập trình | Backend API Server - Django MVT + Service Layer, MySQL |
| 3 | Các loại user | Quản lý: ql001 / MyChi@123 — Lễ tân: lt001 / Chuyen@123 |
| 4 | Số lượng chức năng | 9 nhóm chức năng, 39 endpoint |
| 5 | Chức năng hài lòng nhất | Đặt phòng và check-out |
| 6 | Số lượng các API | Khoảng 77 thao tác API |
| 7 | API hài lòng nhất | `POST /api/bookings/`: Tự động tính giá, lập Invoice — `PUT /api/bookings/<id>/check-out/`: Cập nhật Invoice — `POST /api/pricing/calculate-booking-price/`: Ước tính giá trước khi đặt |
| 8 | Kiểm thử | Postman (2 luồng: 8 bước Quản lý + 11 bước Lễ tân) + 136 Unit/API test case + 2 E2E script |

---

## PHỤ LỤC HÌNH

Các hình trong phụ lục dùng để minh chứng kết quả kiểm thử các API chính của hệ thống bằng Postman.

**Kiểm thử API đăng nhập bằng Postman**

[TODO-HÌNH]

**Hình 8. Kiểm thử API đăng nhập bằng Postman**

Hình 8 cho thấy API đăng nhập trả về kết quả thành công và phản hồi dữ liệu ở dạng JSON.

---

**Kiểm thử API xem danh sách phòng bằng Postman**

[TODO-HÌNH]

**Hình 9. Kiểm thử API xem danh sách phòng bằng Postman**

Hình 9 cho thấy hệ thống trả về danh sách phòng từ cơ sở dữ liệu, gồm các thông tin như số phòng, loại phòng, tầng và trạng thái phòng.

---

**Kiểm thử API tạo đặt phòng bằng Postman**

[TODO-HÌNH]

**Hình 10. Kiểm thử API tạo đặt phòng bằng Postman**

Hình 10 cho thấy hệ thống tạo đặt phòng thành công và lưu thông tin booking vào cơ sở dữ liệu.

---

**Kiểm thử API check-in bằng Postman**

[TODO-HÌNH]

**Hình 11. Kiểm thử API check-in bằng Postman**

Hình 11 cho thấy hệ thống cập nhật trạng thái booking sang đang ở và chuyển trạng thái phòng sang có khách.

---

**Kiểm thử API thanh toán hóa đơn bằng Postman**

[TODO-HÌNH]

**Hình 12. Kiểm thử API thanh toán hóa đơn bằng Postman**

Hình 12 cho thấy hóa đơn được cập nhật sang trạng thái đã thanh toán, kèm phương thức và thời gian thanh toán.

---

## PHỤ LỤC DANH SÁCH API THEO ENDPOINT

Hệ thống có 39 endpoint chính và khoảng 77 thao tác API.

| STT | Nhóm API | Endpoint | Method | Chức năng |
|:---:|---|---|---|---|
| 1 | Xác thực | `/api/auth/register/` | POST | Đăng ký tài khoản mới. Tài khoản mặc định role le_tan, is_active=False. |
| 2 | | `/api/auth/login/` | POST | Đăng nhập hệ thống. |
| 3 | | `/api/auth/logout/` | POST | Đăng xuất khỏi hệ thống. |
| 4 | | `/api/auth/profile/` | GET, PUT | Xem và cập nhật thông tin tài khoản đang đăng nhập. |
| 5 | | `/api/auth/change-password/` | PUT | Đổi mật khẩu tài khoản. |
| 6 | Tài khoản | `/api/users/` | GET, POST | Xem danh sách tài khoản và tạo tài khoản mới. |
| 7 | | `/api/users/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa tài khoản. |
| 8 | | `/api/users/<id>/disable/` | POST | Vô hiệu hóa tài khoản. |
| 9 | | `/api/users/<id>/enable/` | POST | Kích hoạt lại tài khoản. |
| 10 | Phòng ban | `/api/departments/` | GET, POST | Xem danh sách và thêm phòng ban. |
| 11 | | `/api/departments/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa phòng ban. |
| 12 | Nhân viên | `/api/employees/` | GET, POST | Xem danh sách và thêm nhân viên. |
| 13 | | `/api/employees/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa nhân viên. |
| 14 | Khách hàng | `/api/customers/` | GET, POST | Xem danh sách, lọc/tìm kiếm và thêm khách hàng. |
| 15 | | `/api/customers/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa khách hàng. |
| 16 | Loại phòng | `/api/room-types/` | GET, POST | Xem danh sách và thêm loại phòng. |
| 17 | | `/api/room-types/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa loại phòng. |
| 18 | Phòng | `/api/rooms/` | GET, POST | Xem danh sách, lọc phòng trống và thêm phòng. |
| 19 | | `/api/rooms/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa phòng. |
| 20 | | `/api/rooms/<id>/status/` | PUT | Cập nhật trạng thái phòng. |
| 21 | Dịch vụ | `/api/services/` | GET, POST | Xem danh sách và thêm dịch vụ. |
| 22 | | `/api/services/<id>/` | GET, PUT, PATCH, DELETE | Xem chi tiết, cập nhật hoặc xóa dịch vụ. |
| 23 | Tính giá | `/api/pricing/calculate-booking-price/` | POST | Ước tính giá phòng theo ngày, loại phòng và loại khách hàng. |
| 24 | Đặt phòng | `/api/bookings/` | GET, POST | Xem danh sách và tạo đặt phòng. |
| 25 | | `/api/bookings/<id>/` | GET, PUT, DELETE | Xem chi tiết, cập nhật ghi chú hoặc hủy đặt phòng. |
| 26 | | `/api/bookings/<id>/confirm/` | PUT | Xác nhận đặt phòng. |
| 27 | | `/api/bookings/<id>/cancel/` | PUT | Hủy đặt phòng. |
| 28 | | `/api/bookings/<id>/check-in/` | PUT | Check-in, cập nhật trạng thái booking và phòng. |
| 29 | | `/api/bookings/<id>/check-out/` | PUT | Check-out và cập nhật trạng thái trả phòng. |
| 30 | Dịch vụ đặt phòng | `/api/bookings/<id>/services/` | GET, POST | Xem và ghi nhận dịch vụ khách sử dụng trong booking. |
| 31 | | `/api/booking-services/<id>/` | PUT, DELETE | Cập nhật hoặc xóa dịch vụ đã ghi nhận trong booking. |
| 32 | Hóa đơn theo booking | `/api/bookings/<id>/invoice/` | GET | Xem hóa đơn theo đặt phòng. |
| 33 | Hóa đơn | `/api/invoices/` | GET, POST | Xem danh sách và lập hóa đơn. |
| 34 | | `/api/invoices/<id>/` | GET | Xem chi tiết hóa đơn. |
| 35 | Thanh toán | `/api/invoices/<id>/pay/` | PUT | Cập nhật trạng thái thanh toán hóa đơn. |
| 36 | Thống kê | `/api/reports/revenue/` | GET | Thống kê doanh thu. |
| 37 | | `/api/reports/room-status/` | GET | Thống kê tình trạng phòng. |
| 38 | | `/api/reports/booking-statistics/` | GET | Thống kê đặt phòng. |
| 39 | | `/api/reports/top-services/` | GET | Thống kê dịch vụ được sử dụng nhiều. |
