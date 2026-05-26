# Giải Thích App Pricing

## 1. Mục đích

`pricing` là app/module nâng cao tách riêng khỏi app chính `hotel_app`.

App chính `hotel_app` quản lý dữ liệu khách sạn như phòng, loại phòng, khách hàng, booking và hóa đơn. App `pricing` không tạo bảng mới, mà đọc dữ liệu `Room` và `RoomType` từ `hotel_app.models` để tính giá booking dự kiến.

Ý nghĩa khi trình bày:

```text
Một Django project có thể có nhiều app.
hotel_app là app nghiệp vụ chính.
pricing là module tính toán riêng.
API trong pricing gọi dữ liệu từ hotel_app nhưng thuật toán tính giá nằm trong pricing/services.py.
```

## 2. Cấu trúc file

```text
pricing/
├── apps.py
├── serializers.py
├── services.py
├── urls.py
├── views.py
└── tests.py
```

Vai trò từng file:

| File | Vai trò |
|---|---|
| `apps.py` | Khai báo Django app `pricing` |
| `urls.py` | Đăng ký route cho API pricing |
| `views.py` | Nhận request, gọi serializer và gọi service tính giá |
| `serializers.py` | Validate dữ liệu đầu vào |
| `services.py` | Chứa thuật toán tính giá booking |
| `tests.py` | Kiểm thử API và service của pricing |

## 3. Cách nối vào project chính

Trong `config/settings.py`:

```python
'pricing.apps.PricingConfig',
```

Trong `config/urls.py`:

```python
path('api/pricing/', include('pricing.urls')),
```

Nhờ đó API của app `pricing` có prefix:

```text
/api/pricing/
```

## 4. API sử dụng

Endpoint:

```text
POST /api/pricing/calculate-booking-price/
```

Body:

```json
{
  "room_id": 16,
  "check_in": "2028-08-10",
  "check_out": "2028-08-13",
  "customer_type": "vip"
}
```

Điều kiện:

- Người dùng phải đăng nhập.
- `room_id` phải tồn tại trong bảng `Room`.
- `check_out` phải sau `check_in`.
- `customer_type` là `regular` hoặc `vip`.

## 5. Luồng xử lý

```text
Client/Postman
-> POST /api/pricing/calculate-booking-price/
-> config/urls.py
-> pricing/urls.py
-> PricingViewSet.calculate_booking_price()
-> BookingPriceSerializer validate dữ liệu
-> BookingPriceCalculator.lay_phong()
-> đọc Room và RoomType từ hotel_app.models
-> BookingPriceCalculator.tinh_gia()
-> trả JSON bằng api_response()
```

## 6. Công thức tính giá

Trong `pricing/services.py`, class chính là:

```python
class BookingPriceCalculator:
```

Các quy tắc:

```text
so_dem = check_out - check_in
base_price = price_per_night * so_dem
weekend_fee = price_per_night * 10% * so_dem_cuoi_tuan
vip_discount = 10% * (base_price + weekend_fee) nếu customer_type = vip
final_price = base_price + weekend_fee - vip_discount
```

Ví dụ:

```text
Phòng giá 500000/đêm
Ở 3 đêm
Có 2 đêm cuối tuần
Khách VIP

base_price = 500000 * 3 = 1500000
weekend_fee = 500000 * 10% * 2 = 100000
vip_discount = (1500000 + 100000) * 10% = 160000
final_price = 1500000 + 100000 - 160000 = 1440000
```

## 7. Response mẫu

```json
{
  "message": "Tính giá booking thành công",
  "data": {
    "room_id": 16,
    "room_number": "104",
    "room_type": "Standard",
    "customer_type": "vip",
    "check_in": "2028-08-10",
    "check_out": "2028-08-13",
    "so_dem": 3,
    "weekend_nights": 2,
    "price_per_night": 500000.0,
    "base_price": 1500000.0,
    "weekend_fee": 100000.0,
    "vip_discount": 160000.0,
    "final_price": 1440000.0,
    "formula": "final_price = base_price + weekend_fee - vip_discount"
  }
}
```

## 8. Cách dùng trong app chính

Hiện tại `pricing` được expose thành API riêng để demo rõ việc app chính gọi module tính toán riêng.

Nếu muốn dùng trực tiếp trong nghiệp vụ booking, `hotel_app/services/booking_service.py` có thể import:

```python
from pricing.services import BookingPriceCalculator
```

Sau đó gọi:

```python
calculator = BookingPriceCalculator()
room = calculator.lay_phong(room_id)
price_data, err_msg = calculator.tinh_gia(
    room,
    check_in,
    check_out,
    customer_type,
)
```

Như vậy `hotel_app` vẫn quản lý booking, còn `pricing` chịu trách nhiệm tính giá.

## 9. Cách demo

1. Đăng nhập:

```text
POST /api/auth/login/
```

2. Gọi API pricing:

```text
POST /api/pricing/calculate-booking-price/
```

3. Mở Postman collection:

```text
docs/hotel_management_postman_collection.json
```

Request đã có sẵn:

```text
12 - Pricing Calculate Booking Price
```

## 10. Câu trả lời khi thầy hỏi

```text
Dự án có nhiều app trong cùng một Django project.
hotel_app là app chính quản lý khách sạn.
pricing là app nâng cao xử lý thuật toán tính giá booking.
PricingViewSet chỉ nhận request và validate dữ liệu.
Thuật toán tính giá nằm trong BookingPriceCalculator của pricing/services.py.
Module pricing đọc Room và RoomType từ hotel_app.models để tính giá dự kiến.
```
