-- ============================================================
-- FILE 02: THÊM DỮ LIỆU MẪU
-- Đề tài: Web API Quản lý Khách sạn nội bộ
-- Database: hotel_management
-- ============================================================

USE hotel_management;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE BookingService;
TRUNCATE TABLE Invoice;
TRUNCATE TABLE Booking;
TRUNCATE TABLE Service;
TRUNCATE TABLE Room;
TRUNCATE TABLE RoomType;
TRUNCATE TABLE Customer;
TRUNCATE TABLE Employee;
TRUNCATE TABLE Department;
TRUNCATE TABLE `User`;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 1. USER
-- Role: quan_ly / le_tan
-- Mat khau demo:
-- ql001 / MyChi@123
-- lt001 / Chuyen@123
-- lt002 / DucMinh@123
-- Cac tai khoan lt003-lt006 dung mat khau demo: 123456
-- Gia tri cot password la hash pbkdf2_sha256 cua Django.
-- ============================================================

INSERT INTO `User` 
(id, username, password, email, role, is_active) 
VALUES
(1, 'ql001', 'pbkdf2_sha256$1200000$TIzBdapSpY71TxwXIbCq2y$y8dEgDXRrgMn6naEHIjApU9ISGRGFRSCHaxrRqgaGJM=', 'mychi@hotel.vn',       'quan_ly', 1),
(2, 'lt001', 'pbkdf2_sha256$1200000$jQOqWoxWkU42eZbKK2OXMA$tb3TLzFkNAabXXt6bWCqPKZsMHMNDwThXA22e3iEniI=', 'chuyen@hotel.vn',      'le_tan',  1),
(3, 'lt002', 'pbkdf2_sha256$1200000$nMg1YxEeiQ71QczAVWtBaR$OLsEr5QlUxwczMQvp1IkWIwfCcV6WoLm/Z4aIa8EvPU=', 'ducminh@hotel.vn',     'le_tan',  1),
(4, 'lt003', 'pbkdf2_sha256$1200000$0ubMRYuiTDlnDNG5tiHxWF$D80mgJdBHmD5ALTBQ8sqZe9O2h4eDxht2AAUkmo84TY=', 'trantanqui@hotel.vn',  'le_tan',  1),
(5, 'lt004', 'pbkdf2_sha256$1200000$3klZyIiMIS8n2O5v1hwA5t$lAYhC3I/lBrD/5bDFS39PpZ2ls03zd7BCTCDqHmaB3w=', 'phamanhtai@hotel.vn',  'le_tan',  1),
(6, 'lt005', 'pbkdf2_sha256$1200000$yKNHNh8gS6efNiIrSeH9QY$z9W9DAFodW2puRc7247kefLXCH+Pte57ra7SB/A1/Vs=', 'thanhtung@hotel.vn',   'le_tan',  1),
(7, 'lt006', 'pbkdf2_sha256$1200000$PmTQCQO09VzO79sN5Nryvx$oK5ohk0m45/nN0r0lQMbd+kA8P9Ro4gSnoKFPBYGRQw=', 'minhhoang@hotel.vn',   'le_tan',  1);

-- ============================================================
-- 2. DEPARTMENT
-- ============================================================

INSERT INTO Department 
(id, name, description) 
VALUES
(1, 'Quản lý', 'Quản lý chung hoạt động khách sạn và theo dõi báo cáo'),
(2, 'Lễ tân', 'Tiếp nhận khách, tạo đặt phòng, check-in, check-out và thanh toán'),
(3, 'Buồng phòng', 'Dọn dẹp, kiểm tra và cập nhật tình trạng phòng'),
(4, 'Dịch vụ', 'Quản lý các dịch vụ sử dụng thêm trong khách sạn'),
(5, 'Kế toán', 'Theo dõi hóa đơn, doanh thu và tình trạng thanh toán');

-- ============================================================
-- 3. EMPLOYEE
-- ============================================================

INSERT INTO Employee 
(id, user_id, department_id, full_name, phone, salary, hire_date, shift, status) 
VALUES
(1, 1, 1, 'Trịnh Thị Mỹ Chi',  '0901000001', 15000000, '2024-01-10', 'sang',  'dang_lam'),
(2, 2, 2, 'Võ Mộng Chuyền',   '0901000002',  9000000, '2024-02-15', 'sang',  'dang_lam'),
(3, 3, 2, 'Lê Đức Minh',      '0901000003',  9000000, '2024-03-01', 'chieu', 'dang_lam'),
(4, 4, 2, 'Trần Tấn Quí',     '0901000004',  8500000, '2024-04-05', 'sang',  'dang_lam'),
(5, 5, 2, 'Phạm Anh Tài',     '0901000005',  8500000, '2024-04-12', 'chieu', 'dang_lam'),
(6, 6, 3, 'Trần Thanh Tùng',  '0901000006',  8200000, '2024-05-10', 'sang',  'dang_lam'),
(7, 7, 4, 'Võ Minh Hoàng',    '0901000007',  8800000, '2024-06-01', 'toi',   'dang_lam');

-- ============================================================
-- 4. CUSTOMER
-- customer_type: regular / vip
-- ============================================================

INSERT INTO Customer 
(id, full_name, phone, email, id_card, address, customer_type) 
VALUES
(1,  'Nguyễn Tất Hưng',    '0911000001', 'nguyentathung@gmail.com',  '079206000001', 'Quận Phú Nhuận, TP. Hồ Chí Minh', 'regular'),
(2,  'Phạm Quốc Anh',      '0911000002', 'phamquocanh@gmail.com',    '079206000002', 'Quận 7, TP. Hồ Chí Minh', 'regular'),
(3,  'Đặng Thị Ý Loan',    '0911000003', 'dangthiyloan@gmail.com',   '079206000003', 'Quận 5, TP. Hồ Chí Minh', 'vip'),
(4,  'Lê Trung Trực',      '0911000004', 'letrungtruc@gmail.com',    '079206000004', 'Quận 11, TP. Hồ Chí Minh', 'regular'),
(5,  'Hàng Tuấn Thiên',    '0911000005', 'hangtuanthien@gmail.com',  '079206000005', 'Quận 1, TP. Hồ Chí Minh', 'vip'),
(6,  'Nguyễn Văn Dũng',    '0911000006', 'nguyenvandung@gmail.com',  '079206000006', 'Quận 12, TP. Hồ Chí Minh', 'regular'),
(7,  'Dư Đức Long',        '0911000007', 'duduclong@gmail.com',      '079206000007', 'Quận Tân Phú, TP. Hồ Chí Minh', 'regular'),
(8,  'Nguyễn Thị Mai',     '0911000008', NULL,                       '079206000008', 'Quận Bình Thạnh, TP. Hồ Chí Minh', 'regular'),
(9,  'Lâm Gia Huy',        '0911000009', NULL,                       '079206000009', 'Quận 3, TP. Hồ Chí Minh', 'vip'),
(10, 'Hoàng Kim Ngân',     '0911000010', NULL,                       '079206000010', 'Quận Gò Vấp, TP. Hồ Chí Minh', 'regular');

-- ============================================================
-- 5. ROOMTYPE
-- ============================================================

INSERT INTO RoomType 
(id, name, price_per_night, capacity, description) 
VALUES
(1, 'Standard', 500000, 2, 'Phòng tiêu chuẩn, phù hợp khách lưu trú ngắn ngày'),
(2, 'Superior', 650000, 2, 'Phòng rộng hơn Standard, có bàn làm việc và cửa sổ lớn'),
(3, 'Deluxe', 800000, 2, 'Phòng cao cấp, nội thất đẹp, phù hợp khách du lịch hoặc công tác'),
(4, 'Suite', 1500000, 3, 'Phòng rộng, có khu vực tiếp khách riêng'),
(5, 'VIP', 2500000, 4, 'Phòng cao cấp nhất, phù hợp khách VIP hoặc gia đình');

-- ============================================================
-- 6. ROOM
-- status: trong / co_khach / bao_tri
-- ============================================================

INSERT INTO Room 
(id, room_type_id, room_number, floor, status) 
VALUES
(1,  1, '101', 1, 'trong'),
(2,  1, '102', 1, 'trong'),
(3,  1, '103', 1, 'co_khach'),
(4,  2, '201', 2, 'trong'),
(5,  2, '202', 2, 'co_khach'),
(6,  2, '203', 2, 'bao_tri'),
(7,  3, '301', 3, 'trong'),
(8,  3, '302', 3, 'co_khach'),
(9,  3, '303', 3, 'trong'),
(10, 4, '401', 4, 'trong'),
(11, 4, '402', 4, 'co_khach'),
(12, 4, '403', 4, 'trong'),
(13, 5, '501', 5, 'trong'),
(14, 5, '502', 5, 'co_khach'),
(15, 5, '503', 5, 'bao_tri'),
(16, 1, '104', 1, 'trong'),
(17, 2, '204', 2, 'trong'),
(18, 3, '304', 3, 'trong'),
(19, 4, '404', 4, 'trong'),
(20, 5, '504', 5, 'trong');

-- ============================================================
-- 7. SERVICE
-- is_active: 1 = đang sử dụng, 0 = ngừng sử dụng
-- ============================================================

INSERT INTO Service 
(id, name, price, description, is_active) 
VALUES
(1, 'Ăn sáng buffet', 150000, 'Buffet sáng từ 6h30 đến 9h30', 1),
(2, 'Giặt ủi', 80000, 'Dịch vụ giặt ủi theo kg', 1),
(3, 'Đưa đón sân bay', 250000, 'Xe đưa đón sân bay Tân Sơn Nhất', 1),
(4, 'Thuê xe máy', 200000, 'Thuê xe máy theo ngày', 1),
(5, 'Spa & Massage', 350000, 'Gói massage thư giãn 60 phút', 1),
(6, 'Minibar', 50000, 'Nước uống và đồ ăn nhẹ trong phòng', 1),
(7, 'Phòng họp', 500000, 'Dịch vụ sử dụng phòng họp theo buổi', 1),
(8, 'Giường phụ', 120000, 'Giường phụ cho khách lưu trú thêm', 1),
(9, 'Trang trí sinh nhật', 300000, 'Trang trí phòng theo yêu cầu sinh nhật', 1),
(10, 'Trả phòng muộn', 200000, 'Phí hỗ trợ trả phòng muộn', 1);

-- ============================================================
-- 8. BOOKING
-- created_by_id là nhân viên tạo booking
-- status: cho_xac_nhan / da_xac_nhan / dang_o / da_tra_phong / da_huy
-- ============================================================

INSERT INTO Booking 
(id, customer_id, room_id, check_in, check_out, status, note, created_by_id) 
VALUES
(1,  1,  7,  '2026-06-01', '2026-06-04', 'dang_o',       'Khách yêu cầu phòng tầng cao', 2),
(2,  2,  13, '2026-06-02', '2026-06-05', 'dang_o',       'Khách đặt phòng VIP cho chuyến công tác', 3),
(3,  5,  10, '2026-05-20', '2026-05-24', 'da_tra_phong', 'Khách hàng VIP, ưu tiên hỗ trợ nhanh', 2),
(4,  3,  14, '2026-06-10', '2026-06-12', 'da_xac_nhan',  'Khách hàng VIP đặt trước', 3),
(5,  8,  1,  '2026-05-23', '2026-05-24', 'da_tra_phong', 'Khách đặt trực tiếp tại quầy', 2),
(6,  9,  15, '2026-07-01', '2026-07-03', 'cho_xac_nhan', 'Khách VIP cần xác nhận lại', 3),
(7,  4,  4,  '2026-06-05', '2026-06-06', 'da_xac_nhan',  'Khách yêu cầu check-in sớm', 2),
(8,  6,  8,  '2026-06-15', '2026-06-18', 'dang_o',       'Khách sử dụng thêm dịch vụ thuê xe', 2),
(9,  7,  11, '2026-05-10', '2026-05-12', 'da_tra_phong', 'Khách thanh toán bằng chuyển khoản', 3),
(10, 10, 2,  '2026-06-20', '2026-06-21', 'da_huy',       'Khách hủy do thay đổi lịch trình', 2),
(11, 1,  18, '2026-07-05', '2026-07-08', 'cho_xac_nhan', 'Đặt phòng tại quầy, chờ xác nhận', 3),
(12, 2,  20, '2026-07-10', '2026-07-12', 'da_xac_nhan',  'Khách yêu cầu phòng yên tĩnh', 2);

-- ============================================================
-- 9. BOOKINGSERVICE
-- subtotal = quantity * service.price
-- ============================================================

INSERT INTO BookingService 
(id, booking_id, service_id, quantity, subtotal) 
VALUES
(1, 1, 1, 2, 300000),
(2, 1, 3, 1, 250000),
(3, 2, 5, 1, 350000),
(4, 2, 6, 4, 200000),
(5, 3, 1, 4, 600000),
(6, 3, 2, 2, 160000),
(7, 3, 5, 1, 350000),
(8, 4, 3, 1, 250000),
(9, 4, 1, 2, 300000),
(10, 6, 5, 2, 700000),
(11, 6, 6, 6, 300000),
(12, 8, 4, 3, 600000),
(13, 9, 1, 2, 300000);

-- ============================================================
-- 10. INVOICE
-- payment_status: chua_thanh_toan / da_thanh_toan
-- payment_method: tien_mat / chuyen_khoan / the
-- ============================================================

INSERT INTO Invoice 
(id, booking_id, room_charge, service_charge, total, payment_status, payment_method, paid_at) 
VALUES
(1,  1, 2400000,  550000, 2950000, 'chua_thanh_toan', NULL, NULL),
(2,  2, 7500000,  550000, 8050000, 'chua_thanh_toan', NULL, NULL),
(3,  3, 6000000, 1110000, 7110000, 'da_thanh_toan', 'chuyen_khoan', '2026-05-24 10:15:00'),
(4,  4, 5000000,  550000, 5550000, 'chua_thanh_toan', NULL, NULL),
(5,  5,  500000,       0,  500000, 'da_thanh_toan', 'tien_mat', '2026-05-24 08:30:00'),
(6,  6, 5000000, 1000000, 6000000, 'chua_thanh_toan', NULL, NULL),
(7,  7,  650000,       0,  650000, 'chua_thanh_toan', NULL, NULL),
(8,  8, 2400000,  600000, 3000000, 'chua_thanh_toan', NULL, NULL),
(9,  9, 3000000,  300000, 3300000, 'da_thanh_toan', 'chuyen_khoan', '2026-05-12 11:00:00'),
(10, 12, 5000000,      0, 5000000, 'chua_thanh_toan', NULL, NULL);

-- ============================================================
-- RESET AUTO_INCREMENT SAU KHI INSERT ID CỐ ĐỊNH

ALTER TABLE `User` AUTO_INCREMENT = 8;
ALTER TABLE Department AUTO_INCREMENT = 6;
ALTER TABLE Employee AUTO_INCREMENT = 8;
ALTER TABLE Customer AUTO_INCREMENT = 11;
ALTER TABLE RoomType AUTO_INCREMENT = 6;
ALTER TABLE Room AUTO_INCREMENT = 21;
ALTER TABLE Service AUTO_INCREMENT = 11;
ALTER TABLE Booking AUTO_INCREMENT = 13;
ALTER TABLE BookingService AUTO_INCREMENT = 14;
ALTER TABLE Invoice AUTO_INCREMENT = 11;

-- ============================================================
