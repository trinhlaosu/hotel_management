# BÁO CÁO ĐỒ ÁN MÔN HỌC

## XÂY DỰNG RESTFUL API QUẢN LÝ KHÁCH SẠN BẰNG DJANGO REST FRAMEWORK

**Nhóm thực hiện:** Nhóm 04  
**Môn học:** Lập trình Python  
**Thời gian:** 05/2026

| Thành viên | MSSV |
|---|---|
| Trịnh Thị Mỹ Chi | 25410022 |
| Võ Mộng Chuyền | 25410024 |
| Lê Đức Minh | 25410092 |

> Ghi chú cần cập nhật trước khi nộp: phân công chi tiết chính xác theo thực tế và ảnh chụp Postman thật của nhóm.

---

## 1. Giới thiệu

Đề tài xây dựng RESTful API quản lý khách sạn bằng Django Rest Framework nhằm hỗ trợ các nghiệp vụ cơ bản của một khách sạn: quản lý tài khoản, nhân viên, khách hàng, phòng, đặt phòng, sử dụng dịch vụ, lập hóa đơn, thanh toán và thống kê. Sản phẩm tập trung vào phần backend API đúng định hướng đồ án Web API/Backend API Server, không xây dựng giao diện frontend riêng. Việc kiểm thử và minh họa chức năng được thực hiện bằng Postman và bộ test tự động của Django.

Hệ thống được xây dựng bằng Python, Django, Django Rest Framework và MySQL theo kiến trúc Django MVT kết hợp service layer. Nhóm tự phân tích yêu cầu, thiết kế cơ sở dữ liệu và triển khai mã nguồn dựa trên yêu cầu đồ án; không sao chép nguyên mẫu từ Internet. Các tài liệu tham khảo chính là tài liệu chính thức của Django, Django Rest Framework và hướng dẫn môn học. Kết quả đạt được là một hệ thống API có phân quyền, có luồng đặt phòng hoàn chỉnh, có hóa đơn tự động và có kiểm thử cho các chức năng chính.

---

## 2. Mục tiêu và phạm vi

Mục tiêu của đồ án là xây dựng một backend API có thể phục vụ cho hệ thống quản lý khách sạn nội bộ. API trả về dữ liệu JSON, có đăng nhập, phân quyền, kiểm tra dữ liệu đầu vào và xử lý các nghiệp vụ chính thay vì chỉ thao tác CRUD đơn giản.

- Đáp ứng yêu cầu sử dụng ngôn ngữ Python, có cơ sở dữ liệu, có nhiều đối tượng người dùng và có REST API.
- Quản lý dữ liệu nền: tài khoản, phòng ban, nhân viên, khách hàng, loại phòng, phòng và dịch vụ.
- Xử lý nghiệp vụ: tạo booking, xác nhận, hủy, check-in, check-out, ghi nhận dịch vụ, lập và thanh toán hóa đơn.
- Cung cấp API báo cáo doanh thu, trạng thái phòng, thống kê đặt phòng và dịch vụ được dùng nhiều.
- Kiểm thử bằng Unit/API test, E2E test và Postman collection.

---

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ/Công cụ | Vai trò |
|---|---|---|
| Ngôn ngữ | Python | Ngôn ngữ lập trình chính |
| Framework | Django | Xây dựng ứng dụng web backend theo MVT |
| API | Django Rest Framework | Serializer, ViewSet, Router, Response, Permission |
| Cơ sở dữ liệu | MySQL | Lưu trữ dữ liệu nghiệp vụ |
| Lọc dữ liệu | django-filter | Hỗ trợ filter/search/order trong API |
| Kiểm thử | Unit/API test, E2E test, Postman | Kiểm tra tự động và kiểm thử luồng API |

Django Rest Framework được chọn vì phù hợp với yêu cầu REST API: serializer giúp kiểm tra và chuyển đổi dữ liệu, ViewSet giúp tổ chức các API theo tài nguyên, router giúp sinh URL rõ ràng, permission giúp kiểm soát quyền truy cập. Service layer được bổ sung để tách nghiệp vụ khỏi view, giúp code dễ đọc và dễ kiểm thử hơn.

---

## 4. Thiết kế cơ sở dữ liệu

Cơ sở dữ liệu của hệ thống gồm 10 bảng chính. Các bảng được thiết kế xoay quanh hai nhóm dữ liệu: dữ liệu danh mục như phòng ban, loại phòng, phòng, dịch vụ; và dữ liệu nghiệp vụ như khách hàng, đặt phòng, hóa đơn, dịch vụ sử dụng theo booking.

| STT | Bảng | Mô tả |
|---:|---|---|
| 1 | User | Tài khoản đăng nhập, email, mật khẩu đã mã hóa, vai trò và trạng thái hoạt động |
| 2 | Department | Phòng ban trong khách sạn |
| 3 | Employee | Hồ sơ nhân viên, ca làm, lương và liên kết với tài khoản |
| 4 | Customer | Thông tin khách hàng, số điện thoại, CCCD, loại khách |
| 5 | RoomType | Loại phòng, giá theo đêm, sức chứa |
| 6 | Room | Phòng cụ thể, tầng, trạng thái phòng |
| 7 | Booking | Đặt phòng, ngày nhận/trả, trạng thái và nhân viên tạo |
| 8 | Invoice | Hóa đơn, tiền phòng, tiền dịch vụ, tổng tiền, trạng thái thanh toán |
| 9 | Service | Danh mục dịch vụ của khách sạn |
| 10 | BookingService | Dịch vụ khách đã sử dụng trong một booking |

Các quan hệ chính:

- User liên kết một-một với Employee.
- Department liên kết một-nhiều với Employee.
- RoomType liên kết một-nhiều với Room.
- Customer liên kết một-nhiều với Booking.
- Room liên kết một-nhiều với Booking.
- Employee liên kết một-nhiều với Booking thông qua trường `created_by`.
- Booking liên kết một-một với Invoice.
- Booking và Service liên kết nhiều-nhiều thông qua BookingService.

---

## 5. Kiến trúc hệ thống

Hệ thống được tổ chức theo kiến trúc Django MVT, đồng thời áp dụng phong cách REST API của Django Rest Framework. Mỗi request từ client đi qua URL router đến ViewSet, dữ liệu đầu vào được Serializer kiểm tra, nghiệp vụ được xử lý trong Service, dữ liệu được lưu hoặc đọc bằng Model và kết quả trả về dưới dạng JSON thống nhất.

| Lớp | Thành phần trong dự án | Trách nhiệm |
|---|---|---|
| Model | `hotel_app/models.py` | Định nghĩa bảng, quan hệ, ràng buộc và manager |
| Serializer | `hotel_app/serializers/` | Validate dữ liệu request và chuyển model thành JSON |
| ViewSet | `hotel_app/views/` | Nhận request, chọn serializer, gọi service và trả response |
| Service | `hotel_app/services/` | Xử lý nghiệp vụ như booking, invoice, room status, report |
| Core | `core/api.py`, `core/messages.py` | Chuẩn hóa response và thông báo |
| Router | `hotel_app/urls.py` | Đăng ký endpoint API |

Cách tách lớp này giúp code không bị dồn hết vào view. View chủ yếu điều phối request/response, serializer chịu trách nhiệm dữ liệu vào/ra, còn service xử lý quy tắc nghiệp vụ. Đây là cách triển khai phù hợp với DRF thực tế vì giữ được lợi ích của framework nhưng vẫn có lớp nghiệp vụ rõ ràng.

Luồng xử lý tổng quát:

```text
Client/Postman
    -> URL Router
    -> ViewSet
    -> Serializer validate dữ liệu
    -> Service xử lý nghiệp vụ
    -> Model truy cập database
    -> Serializer xuất dữ liệu
    -> Response JSON
```

---

## 6. Chức năng hệ thống

### 6.1. Xác thực và phân quyền

Hệ thống hỗ trợ đăng ký, đăng nhập, đăng xuất, xem/cập nhật hồ sơ cá nhân và đổi mật khẩu. Người dùng được chia thành hai vai trò chính:

| Vai trò | Mô tả | Quyền chính |
|---|---|---|
| `quan_ly` | Quản lý | Quản trị tài khoản, nhân viên, phòng ban, danh mục và xem báo cáo |
| `le_tan` | Lễ tân/Nhân viên | Quản lý khách hàng, phòng, booking, dịch vụ và hóa đơn |
| Guest | Chưa đăng nhập | Đăng ký và đăng nhập |

### 6.2. Quản lý danh mục

Các API CRUD được xây dựng cho tài khoản, phòng ban, nhân viên, khách hàng, loại phòng, phòng và dịch vụ. Một số thao tác xóa được xử lý theo hướng vô hiệu hóa để giữ lịch sử dữ liệu, ví dụ vô hiệu hóa tài khoản hoặc chuyển trạng thái nhân viên sang nghỉ việc.

### 6.3. Đặt phòng

Đây là luồng nghiệp vụ trung tâm của hệ thống. Khi tạo booking, hệ thống kiểm tra phòng có tồn tại, có đang trống và có bị trùng lịch hay không. Sau khi tạo booking, hệ thống có thể xác nhận, hủy, check-in và check-out. Trạng thái phòng được cập nhật theo trạng thái booking để dữ liệu nhất quán.

### 6.4. Dịch vụ và hóa đơn

Trong thời gian khách ở, lễ tân có thể ghi nhận các dịch vụ khách sử dụng. Mỗi dịch vụ được lưu vào BookingService với số lượng và thành tiền. Hóa đơn được tính từ tiền phòng và tiền dịch vụ; khi thanh toán, hệ thống lưu phương thức thanh toán, thời gian thanh toán và chuyển trạng thái hóa đơn sang đã thanh toán.

### 6.5. Báo cáo

Hệ thống có các API báo cáo doanh thu, trạng thái phòng, thống kê booking và top dịch vụ. Nhóm báo cáo giúp quản lý theo dõi tình hình vận hành khách sạn mà không cần truy vấn trực tiếp vào cơ sở dữ liệu.

---

## 7. Danh sách API chính

| Nhóm API | Endpoint chính | Chức năng |
|---|---|---|
| Auth | `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/` | Đăng ký, đăng nhập, đăng xuất |
| User | `/api/users/` | Quản lý tài khoản |
| Department | `/api/departments/` | Quản lý phòng ban |
| Employee | `/api/employees/` | Quản lý nhân viên |
| Customer | `/api/customers/` | Quản lý khách hàng |
| RoomType | `/api/room-types/` | Quản lý loại phòng |
| Room | `/api/rooms/` | Quản lý phòng và trạng thái phòng |
| Service | `/api/services/` | Quản lý dịch vụ |
| Booking | `/api/bookings/` | Tạo, xem, cập nhật booking |
| Booking workflow | `/api/bookings/<id>/confirm/`, `/cancel/`, `/check-in/`, `/check-out/` | Xử lý vòng đời đặt phòng |
| Booking services | `/api/bookings/<id>/services/` | Ghi nhận dịch vụ sử dụng |
| Invoice | `/api/invoices/`, `/api/invoices/<id>/pay/` | Lập và thanh toán hóa đơn |
| Report | `/api/reports/revenue/`, `/room-status/`, `/booking-statistics/`, `/top-services/` | Báo cáo và thống kê |

Tổng số API theo method và endpoint là 64 thao tác, gồm GET, POST, PUT và DELETE. Các endpoint được tổ chức theo tài nguyên nên dễ kiểm thử bằng Postman và dễ mở rộng khi cần xây dựng frontend ở giai đoạn sau.

---

## 8. Luồng nghiệp vụ tiêu biểu

Luồng đặt phòng và thanh toán là chức năng tiêu biểu nhất của hệ thống vì kết hợp nhiều bảng dữ liệu và nhiều lớp xử lý.

1. Người dùng đăng nhập bằng tài khoản quản lý hoặc lễ tân.
2. Lễ tân tìm hoặc tạo thông tin khách hàng.
3. Lễ tân chọn phòng còn trống theo loại phòng, tầng, sức chứa hoặc trạng thái.
4. Hệ thống tạo booking sau khi kiểm tra ngày nhận/trả phòng và kiểm tra trùng lịch.
5. Booking được xác nhận, sau đó khách check-in; trạng thái phòng chuyển sang có khách.
6. Trong thời gian ở, hệ thống ghi nhận dịch vụ khách sử dụng và cập nhật tiền dịch vụ.
7. Khi khách check-out, trạng thái booking chuyển sang đã trả phòng và phòng trở về trạng thái trống.
8. Hóa đơn được lập/cập nhật từ tiền phòng và tiền dịch vụ, sau đó thanh toán theo phương thức đã chọn.

---

## 9. Kiểm thử

Dự án được kiểm thử theo hai hướng: kiểm thử tự động và kiểm thử API bằng Postman. Kiểm thử tự động được chia thành Unit/API test trong `hotel_app/tests/unit/` và E2E test trong `hotel_app/tests/e2e/`. Unit/API test kiểm tra model, service, core utility, view/API, phân quyền, soft delete, validate dữ liệu ngày, cập nhật hóa đơn sau khi sửa/xóa dịch vụ trong booking và các nhánh lỗi quan trọng. E2E test kiểm tra trọn luồng nghiệp vụ từ đăng nhập, tạo khách hàng, đặt phòng, check-in, ghi nhận dịch vụ, check-out, xem hóa đơn, thanh toán đến xem báo cáo doanh thu. Postman collection dùng để minh họa và demo luồng API chính.

| Loại kiểm thử | Kết quả |
|---|---|
| Django system check | Không phát hiện lỗi cấu hình |
| Unit/API test | Kiểm tra các thành phần riêng lẻ và API |
| E2E test | Kiểm tra luồng nghiệp vụ hoàn chỉnh |
| Tổng test tự động | 137 tests chạy thành công |
| Postman | Có collection trong `docs/hotel_management_postman_collection.json` |
| Luồng nghiệp vụ | Đăng nhập - đặt phòng - check-in - dịch vụ - check-out - hóa đơn - thanh toán - báo cáo |

Các ảnh chụp kết quả test API bằng Postman được đưa vào phụ lục để báo cáo chính không bị nặng phần hình ảnh và không vượt quá phạm vi yêu cầu.

---

## 10. Kết luận

Đồ án đã xây dựng được RESTful API quản lý khách sạn bằng Python, Django Rest Framework và MySQL. Hệ thống có cơ sở dữ liệu 10 bảng, có phân quyền người dùng, có các API CRUD, có nghiệp vụ đặt phòng - hóa đơn - thanh toán và có báo cáo thống kê. Code được tổ chức theo kiến trúc Django MVT kết hợp service layer để dễ đọc, dễ kiểm thử và phù hợp hơn với cách dùng DRF trong thực tế.

Chức năng nhóm đánh giá nổi bật nhất là luồng đặt phòng vì nó thể hiện rõ nghiệp vụ khách sạn: kiểm tra phòng trống, quản lý trạng thái booking, cập nhật trạng thái phòng, ghi nhận dịch vụ và tính hóa đơn. Qua đồ án, nhóm hiểu rõ hơn cách xây dựng backend API, cách tách trách nhiệm giữa model, serializer, view và service, cũng như cách kiểm thử API trước khi bàn giao sản phẩm.

---

## Tài liệu tham khảo

1. Django Documentation: https://docs.djangoproject.com/
2. Django REST Framework Documentation: https://www.django-rest-framework.org/
3. Tài liệu và hướng dẫn đồ án môn học Lập trình Python.

---

## Phụ lục A. Phân công công việc

| Thành viên | Nhiệm vụ chính | Kết quả |
|---|---|---|
| Trịnh Thị Mỹ Chi | Phân tích yêu cầu, thiết kế CSDL, chuẩn bị dữ liệu mẫu, rà soát báo cáo | Hoàn thành database, dữ liệu mẫu và tài liệu mô tả |
| Võ Mộng Chuyền | Xây dựng model, serializer, viewset, service và phân quyền API | Hoàn thành các API chính và luồng nghiệp vụ |
| Lê Đức Minh | Viết test, kiểm thử Postman, rà soát lỗi và chuẩn bị demo | Hoàn thành bộ test, Postman collection và kịch bản demo |

---

## Phụ lục B. Tóm tắt kết quả bắt buộc

| Mục | Nội dung |
|---|---|
| Tên đề tài | Xây dựng RESTful API quản lý khách sạn bằng Django Rest Framework |
| Loại sản phẩm | Web API Application / Backend API Server / RESTful API Server |
| Ngôn ngữ | Python |
| Kiến trúc | Django MVT kết hợp service layer |
| Cơ sở dữ liệu | MySQL, 10 bảng chính |
| Đối tượng người dùng | Quản lý, lễ tân, khách chưa đăng nhập |
| Tài khoản mẫu | `ql001/MyChi@123`, `lt001/Chuyen@123`, `lt002/DucMinh@123` |
| Số lượng API | 64 thao tác API theo method + endpoint |
| Chức năng yêu thích | Luồng đặt phòng, check-in/check-out, hóa đơn và thanh toán |
| Kiểm thử | Unit/API test và E2E test 137 tests thành công; có Postman collection |
| Tệp Postman | `docs/hotel_management_postman_collection.json` |

---

## Phụ lục C. Hình ảnh kiểm thử API

Chèn ảnh chụp màn hình Postman thật vào các vị trí sau:

1. Hình C.1. Kết quả đăng nhập thành công trên Postman.
2. Hình C.2. Kết quả tạo booking thành công.
3. Hình C.3. Kết quả xác nhận booking và check-in.
4. Hình C.4. Kết quả ghi nhận dịch vụ cho booking.
5. Hình C.5. Kết quả check-out và xem hóa đơn.
6. Hình C.6. Kết quả thanh toán hóa đơn.
7. Hình C.7. Kết quả API báo cáo doanh thu hoặc trạng thái phòng.

---

## Phụ lục D. Ghi chú nộp bài

- Báo cáo không đặt mục lục, không lời cảm ơn, không đưa mã nguồn vào phần nội dung chính.
- Khi nộp cần bổ sung file PDF xuất từ Word, slide thuyết trình và video demo theo yêu cầu buổi hướng dẫn.
- Trước khi nộp cần bổ sung ảnh chụp Postman thật, xuất PDF từ Word và chuẩn bị slide/video demo theo yêu cầu.
