-- ============================================================
-- FILE 01: TẠO DATABASE VÀ CÁC BẢNG
-- Đề tài: Web API Quản lý Khách sạn nội bộ
-- Database: hotel_management
-- ============================================================

DROP DATABASE IF EXISTS hotel_management;
CREATE DATABASE hotel_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hotel_management;

-- ============================================================
-- 1. USER
-- ============================================================
CREATE TABLE `User` (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'le_tan',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    CONSTRAINT chk_user_role CHECK (role IN ('quan_ly', 'le_tan'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. DEPARTMENT
-- ============================================================
CREATE TABLE Department (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description LONGTEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. EMPLOYEE
-- ============================================================
CREATE TABLE Employee (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    department_id BIGINT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    salary DECIMAL(15,0) NOT NULL DEFAULT 0,
    hire_date DATE NOT NULL,
    shift VARCHAR(20) NOT NULL DEFAULT 'sang',
    status VARCHAR(20) NOT NULL DEFAULT 'dang_lam',

    CONSTRAINT fk_employee_user
        FOREIGN KEY (user_id) REFERENCES `User`(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id) REFERENCES Department(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_employee_shift CHECK (shift IN ('sang', 'chieu', 'toi')),
    CONSTRAINT chk_employee_status CHECK (status IN ('dang_lam', 'nghi_viec'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. CUSTOMER
-- Khách hàng do nhân viên khách sạn nhập và quản lý
-- Map với model: Customer
-- Không có user_id, vì hệ thống dùng nội bộ khách sạn
-- ============================================================
CREATE TABLE Customer (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(254) NULL,
    id_card VARCHAR(20) NOT NULL UNIQUE,
    address LONGTEXT NULL,
    customer_type VARCHAR(20) NOT NULL DEFAULT 'regular',

    CONSTRAINT chk_customer_type CHECK (customer_type IN ('regular', 'vip'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. ROOMTYPE
-- ============================================================
CREATE TABLE RoomType (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    price_per_night DECIMAL(15,0) NOT NULL,
    capacity INT NOT NULL DEFAULT 2,
    description LONGTEXT NULL,

    CONSTRAINT chk_roomtype_price CHECK (price_per_night >= 0),
    CONSTRAINT chk_roomtype_capacity CHECK (capacity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 6. ROOM
-- ============================================================
CREATE TABLE Room (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    room_type_id BIGINT NOT NULL,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    floor INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'trong',

    CONSTRAINT fk_room_roomtype
        FOREIGN KEY (room_type_id) REFERENCES RoomType(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_room_status CHECK (status IN ('trong', 'co_khach', 'bao_tri')),
    CONSTRAINT chk_room_floor CHECK (floor > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 7. BOOKING
-- ============================================================
CREATE TABLE Booking (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    room_id BIGINT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'cho_xac_nhan',
    note LONGTEXT NULL,
    created_by_id BIGINT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_booking_customer
        FOREIGN KEY (customer_id) REFERENCES Customer(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_booking_room
        FOREIGN KEY (room_id) REFERENCES Room(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_booking_employee
        FOREIGN KEY (created_by_id) REFERENCES Employee(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_booking_date CHECK (check_out > check_in),
    CONSTRAINT chk_booking_status CHECK (status IN ('cho_xac_nhan', 'da_xac_nhan', 'dang_o', 'da_tra_phong', 'da_huy'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 8. INVOICE
-- ============================================================
CREATE TABLE Invoice (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    booking_id BIGINT NOT NULL UNIQUE,
    room_charge DECIMAL(15,0) NOT NULL DEFAULT 0,
    service_charge DECIMAL(15,0) NOT NULL DEFAULT 0,
    total DECIMAL(15,0) NOT NULL DEFAULT 0,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'chua_thanh_toan',
    payment_method VARCHAR(20) NULL,
    paid_at DATETIME(6) NULL,

    CONSTRAINT fk_invoice_booking
        FOREIGN KEY (booking_id) REFERENCES Booking(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_invoice_amount CHECK (room_charge >= 0 AND service_charge >= 0 AND total >= 0),
    CONSTRAINT chk_invoice_payment_status CHECK (payment_status IN ('chua_thanh_toan', 'da_thanh_toan')),
    CONSTRAINT chk_invoice_payment_method CHECK (payment_method IS NULL OR payment_method IN ('tien_mat', 'chuyen_khoan', 'the'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 9. SERVICE
-- ============================================================
CREATE TABLE Service (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(15,0) NOT NULL,
    description LONGTEXT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,

    CONSTRAINT chk_service_price CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 10. BOOKINGSERVICE
-- ============================================================
CREATE TABLE BookingService (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    booking_id BIGINT NOT NULL,
    service_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    subtotal DECIMAL(15,0) NOT NULL DEFAULT 0,
    used_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_bookingservice_booking
        FOREIGN KEY (booking_id) REFERENCES Booking(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_bookingservice_service
        FOREIGN KEY (service_id) REFERENCES Service(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_bookingservice_quantity CHECK (quantity > 0),
    CONSTRAINT chk_bookingservice_subtotal CHECK (subtotal >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- INDEX CHO API LỌC/TÌM KIẾM
-- ============================================================
CREATE INDEX idx_user_role ON `User`(role);
CREATE INDEX idx_customer_type ON Customer(customer_type);
CREATE INDEX idx_room_status ON Room(status);
CREATE INDEX idx_booking_status ON Booking(status);
CREATE INDEX idx_booking_dates ON Booking(check_in, check_out);
CREATE INDEX idx_invoice_payment_status ON Invoice(payment_status);
CREATE INDEX idx_service_active ON Service(is_active);

-- ============================================================
