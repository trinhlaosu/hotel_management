# Giải thích app `pricing`

## 1. Tổng quan

`pricing` là Django app độc lập, tách riêng khỏi `hotel_app`, chứa toàn bộ thuật toán tính giá phòng. App này **không tạo bảng CSDL mới** — chỉ đọc `Room` và `RoomType` từ `hotel_app.models` để tính giá.

`BookingPriceCalculator` được gọi tại **4 thời điểm**:

| # | Nơi gọi | Trigger | Mục đích | Dùng kết quả |
|:---:|---|---|---|---|
| 1 | `pricing/views.py` | `POST /api/pricing/calculate-booking-price/` | Ước tính giá trước khi đặt | Toàn bộ dict (trả về client) |
| 2 | `invoice_service.__tinh_tien()` | Tạo booking (`POST /api/bookings/`) | Lập Invoice ban đầu | Chỉ `result['final_price']` |
| 3 | `invoice_service.__tinh_tien()` | Check-out (`PUT /api/bookings/<id>/check-out/`) | Cập nhật Invoice cuối | Chỉ `result['final_price']` |
| 4 | `booking_service.tinh_tien_phong()` | Xem chi tiết booking (`GET /api/bookings/<id>/`) | Hiển thị thông tin tài chính | Chỉ `result['final_price']` |

---

## 2. Cấu trúc file

```
pricing/
├── services.py      # BookingPriceCalculator — toàn bộ thuật toán tính giá
├── serializers.py   # BookingPriceSerializer — validate input API
├── views.py         # PricingViewSet — nhận request, gọi service, trả JSON
└── urls.py          # Đăng ký route /api/pricing/calculate-booking-price/
```

---

## 3. `pricing/services.py` — Chi tiết từng method

### 3.1 Class constants

```python
class BookingPriceCalculator:
    WEEKEND_RATE      = Decimal('0.10')   # phụ thu cuối tuần 10%
    VIP_DISCOUNT_RATE = Decimal('0.10')   # chiết khấu VIP 10%
```

Hai hằng số đặt ở class level → dễ sửa khi thay đổi chính sách giá, không hardcode số trong logic.

---

### 3.2 `lay_phong(room_id)` — Lấy phòng từ DB

```python
def lay_phong(self, room_id):
    try:
        return Room.objects.select_related('room_type').get(
            id=room_id,
            is_deleted=False,
        )
    except Room.DoesNotExist:
        return None
```

- `select_related('room_type')`: JOIN sẵn bảng `RoomType` để tránh N+1 query khi truy cập `room.room_type.price_per_night`
- `is_deleted=False`: lọc phòng bị xóa mềm (soft-delete) — phòng đã xóa không được tính giá
- Trả `None` nếu không tìm thấy → caller kiểm tra và trả 404

**Lưu ý:** method này chỉ được gọi từ `PricingViewSet` (luồng API). Khi `hotel_app` gọi nội bộ (luồng 2-4), object `room` đã có sẵn từ `booking.room`, nên không cần gọi `lay_phong()` nữa.

---

### 3.3 `_count_weekend_nights(check_in, check_out)` — Đếm đêm cuối tuần

```python
def _count_weekend_nights(self, check_in, check_out):
    current = check_in
    count = 0
    while current < check_out:
        if current.weekday() in [5, 6]:   # 5=Thứ 7, 6=Chủ nhật
            count += 1
        current += timedelta(days=1)
    return count
```

Duyệt từng ngày trong khoảng `[check_in, check_out)` (check_out không tính vì đó là ngày trả phòng, không phải đêm ở).

**Ví dụ** — check_in = Thứ 6 (2028-08-11), check_out = Thứ 2 (2028-08-14):

| Ngày | weekday() | Tính? |
|---|---|---|
| 2028-08-11 Thứ 6 | 4 | Không |
| 2028-08-12 Thứ 7 | 5 | **Có** |
| 2028-08-13 Chủ nhật | 6 | **Có** |

→ `weekend_nights = 2`

---

### 3.4 `tinh_gia(room, check_in, check_out, customer_type)` — Tính giá

```python
def tinh_gia(self, room, check_in, check_out, customer_type='regular'):
    so_dem = (check_out - check_in).days
    if so_dem <= 0:
        return None, msg.CHECKOUT_AFTER_CHECKIN

    price_per_night = Decimal(room.room_type.price_per_night)
    weekend_nights  = self._count_weekend_nights(check_in, check_out)
    base_price      = price_per_night * so_dem
    weekend_fee     = price_per_night * self.WEEKEND_RATE * weekend_nights
    subtotal        = base_price + weekend_fee
    vip_discount    = (
        subtotal * self.VIP_DISCOUNT_RATE
        if customer_type == 'vip' else Decimal('0')
    )
    final_price = subtotal - vip_discount

    return { ... }, None
```

**Từng bước tính giá:**

| Bước | Công thức | Ghi chú |
|---|---|---|
| Số đêm | `so_dem = (check_out − check_in).days` | ≤ 0 → lỗi |
| Giá cơ bản | `base_price = price_per_night × so_dem` | Mọi khách |
| Đêm cuối tuần | đếm `weekday() in [5, 6]` | Duyệt từng ngày |
| Phụ thu | `weekend_fee = price_per_night × 10% × weekend_nights` | Mọi khách |
| Tạm tính | `subtotal = base_price + weekend_fee` | Trước chiết khấu |
| Chiết khấu VIP | `vip_discount = subtotal × 10%` nếu `vip`, ngược lại = 0 | Chỉ khách VIP |
| Thành tiền | `final_price = subtotal − vip_discount` | Giá cuối |

**Ví dụ** — phòng 500.000 đ/đêm, ở 3 đêm (2 đêm cuối tuần), khách VIP:

```
base_price   = 500.000 × 3                      = 1.500.000
weekend_fee  = 500.000 × 10% × 2               =   100.000
subtotal     = 1.500.000 + 100.000              = 1.600.000
vip_discount = 1.600.000 × 10%                 =   160.000
final_price  = 1.600.000 − 160.000             = 1.440.000
```

**Kết quả trả về** là một dict với đầy đủ thông tin:

```python
return {
    'room_id': room.id,
    'room_number': room.room_number,
    'room_type': room.room_type.name,
    'customer_type': customer_type,
    'check_in': str(check_in),
    'check_out': str(check_out),
    'so_dem': so_dem,
    'weekend_nights': weekend_nights,
    'price_per_night': float(price_per_night),
    'base_price': float(base_price),
    'weekend_fee': float(weekend_fee),
    'vip_discount': float(vip_discount),
    'final_price': float(final_price),
    'formula': 'final_price = base_price + weekend_fee - vip_discount',
}, None
```

Caller nội bộ chỉ lấy `result['final_price']` — toàn bộ breakdown chỉ dùng khi trả về API.

---

## 4. `pricing/serializers.py` — Validate input

```python
class BookingPriceSerializer(serializers.Serializer):
    room_id       = serializers.IntegerField(min_value=1)
    check_in      = serializers.DateField()
    check_out     = serializers.DateField()
    customer_type = serializers.ChoiceField(
        choices=['regular', 'vip'],
        required=False,
        default='regular',
    )

    def validate(self, attrs):
        ok, err_msg = kiem_tra_ngay(attrs.get('check_in'), attrs.get('check_out'))
        if not ok:
            raise serializers.ValidationError(err_msg)
        return attrs
```

- `customer_type` là **không bắt buộc** (`required=False`) — mặc định `regular`
- `kiem_tra_ngay()` từ `core/validators.py` kiểm tra `check_out > check_in` (cross-field validation)
- Serializer này chỉ dùng cho luồng API (luồng 1) — 3 luồng nội bộ không qua serializer

---

## 5. `pricing/views.py` — Luồng API

```python
class PricingViewSet(viewsets.ViewSet):
    permission_classes = [SessionAuthenticated]

    @action(detail=False, methods=['post'], url_path='calculate-booking-price')
    def calculate_booking_price(self, request):
        serializer = BookingPriceSerializer(data=request.data)
        if not serializer.is_valid():
            return serializer_error_response(serializer)

        calculator = BookingPriceCalculator()
        room = calculator.lay_phong(serializer.validated_data['room_id'])
        if not room:
            return api_response(error=msg.ROOM_NOT_FOUND, status=404)

        data, err_msg = calculator.tinh_gia(
            room,
            serializer.validated_data['check_in'],
            serializer.validated_data['check_out'],
            serializer.validated_data['customer_type'],
        )
        if err_msg:
            return api_response(error=err_msg, status=400)
        return api_response(data=data, message=msg.PRICING_CALCULATED)
```

**Luồng xử lý:**

```
POST /api/pricing/calculate-booking-price/
  → BookingPriceSerializer.is_valid()
      ├── room_id ≥ 1, check_in/check_out là DateField
      └── kiem_tra_ngay(): check_out > check_in
  → calculator.lay_phong(room_id)
      └── Room.objects.get(id=room_id, is_deleted=False)  [404 nếu không có]
  → calculator.tinh_gia(room, check_in, check_out, customer_type)
      └── trả full dict breakdown
  → api_response(data=dict, message="Tính giá booking thành công")
```

**Quyền truy cập:** `SessionAuthenticated` — chỉ cần đăng nhập (cả `quan_ly` lẫn `le_tan`).

---

## 6. Cách `hotel_app` gọi `pricing` nội bộ

Cả 3 luồng nội bộ đều import lazy (tránh circular import) và chỉ lấy `final_price`:

### Luồng 2 & 3 — Qua `InvoiceService.__tinh_tien()`

```python
# hotel_app/services/invoice_service.py
def __tinh_tien(self, booking):
    from pricing.services import BookingPriceCalculator
    customer_type = booking.customer.customer_type
    result, _ = BookingPriceCalculator().tinh_gia(
        booking.room, booking.check_in, booking.check_out, customer_type
    )
    tien_phong = result['final_price']          # chỉ lấy final_price
    ds_dv   = BookingService.objects.filter(booking_id=booking.id)
    tien_dv = sum(float(dv.subtotal) for dv in ds_dv)
    return tien_phong, tien_dv
```

- **Luồng 2:** `tao_hoa_don(booking)` → gọi `__tinh_tien()` → `Invoice.objects.get_or_create(...)`
- **Luồng 3:** `cap_nhat_hoa_don(booking)` → gọi `__tinh_tien()` → `inv.room_charge = tien_phong; inv.save()`

### Luồng 4 — Qua `BookingService.tinh_tien_phong()`

```python
# hotel_app/services/booking_service.py
def tinh_tien_phong(self, booking):
    from pricing.services import BookingPriceCalculator
    customer_type = booking.customer.customer_type
    result, _ = BookingPriceCalculator().tinh_gia(
        booking.room, booking.check_in, booking.check_out, customer_type
    )
    return result['final_price']                # chỉ lấy final_price
```

Được gọi bởi `thong_tin_tai_chinh()`:

```python
def thong_tin_tai_chinh(self, booking):
    return {
        'so_dem':     self.tinh_so_dem(booking.check_in, booking.check_out),
        'tien_phong': self.tinh_tien_phong(booking),   # ← gọi pricing ở đây
        'tien_dv':    self.tinh_tien_dich_vu(booking.id),
    }
```

→ Kết quả trả về trong `GET /api/bookings/<id>/` response.

---

## 7. So sánh luồng API vs nội bộ

| | Luồng API (1) | Luồng nội bộ (2, 3, 4) |
|---|---|---|
| Vào qua | `POST /api/pricing/...` | Gọi trực tiếp từ service |
| Qua Serializer? | Có — validate input | Không |
| Gọi `lay_phong()`? | **Có** — cần tra DB từ `room_id` | **Không** — `booking.room` đã có |
| Kết quả dùng | Toàn bộ dict → trả client | Chỉ `result['final_price']` |
| Import | Trực tiếp ở đầu file | Lazy import trong method |

---

## 8. Điểm cần nhớ khi trình bày

- `pricing` là **app riêng**, không phải file trong `hotel_app`
- **Không có bảng CSDL riêng** — chỉ đọc `Room`, `RoomType` từ `hotel_app`
- Được gọi **4 lần**: 1 qua API (ước tính) + 3 nội bộ (tạo booking, check-out, xem chi tiết)
- Luồng nội bộ **bỏ qua** `lay_phong()` vì `booking.room` đã được `select_related` trước
- `customer_type` là tham số **không bắt buộc** — mặc định `regular`, chỉ `vip` mới có chiết khấu
- Chiết khấu VIP tính trên `subtotal` (đã gồm phụ thu cuối tuần), **không** phải trên `base_price`
- Toàn bộ công thức giá chỉ nằm ở **một nơi duy nhất** — `pricing/services.py`
