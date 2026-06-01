# Các Điểm Nổi Bật — Đồ Án Quản Lý Khách Sạn
**Nhóm 04 | Môn: Lập trình Python**

---

## 1. Kiến Trúc 3 Tầng Rõ Ràng

```
Request → ViewSet (API Layer)
              ↓
          Service Layer (Business Logic)
              ↓
          Model / ORM (Data Layer) → MySQL
```

- **11 ViewSet** xử lý HTTP request/response, không chứa logic nghiệp vụ
- **8 Service class** chứa toàn bộ business logic, tách biệt hoàn toàn
- **10 Model** ánh xạ trực tiếp với bảng DB
- App `pricing` tách riêng để đóng gói thuật toán tính giá
- App `core` chứa tiện ích dùng chung (response, exception, validator, messages)

---

## 2. OOP — Áp Dụng Đầy Đủ Các Khái Niệm

### Abstract Base Class + Kế thừa

```python
# hotel_app/models.py
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        abstract = True  # không tạo bảng DB

# Tất cả 10 model đều kế thừa:
class User(TimestampedModel): ...
class Room(TimestampedModel): ...
class Booking(TimestampedModel): ...
```

### Override (Ghi đè phương thức)

```python
# core/api.py — ApiResponseModelViewSet ghi đè toàn bộ CRUD
class ApiResponseModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs): ...      # override
    def retrieve(self, request, *args, **kwargs): ...  # override
    def create(self, request, *args, **kwargs): ...    # override
    def update(self, request, *args, **kwargs): ...    # override
    def destroy(self, request, *args, **kwargs): ...   # override → soft delete
    def perform_destroy(self, instance):
        instance.is_deleted = True                     # không xóa thật
        instance.save()

# hotel_app/models.py — Custom Manager ghi đè get_queryset()
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
```

### Encapsulation + Composition

```python
# hotel_app/services/booking_service.py
class BookingService:
    def __init__(self):
        self._room_service = RoomService()  # inject dependency (composition)
```

### @property — Thuộc tính tính toán

```python
# hotel_app/models.py
class User(TimestampedModel):
    @property
    def is_authenticated(self): return True

    @property
    def is_anonymous(self):     return False

# hotel_app/services/booking_service.py
@property
def ten_service(self):
    return 'BookingService'
```

### Kế thừa từ DRF Framework

```python
class SessionUserAuthentication(BaseAuthentication): ...  # tùy chỉnh xác thực
class SessionAuthenticated(BasePermission): ...           # quyền đăng nhập
class ManagerOnly(BasePermission): ...                    # quyền quản lý
class SessionNotAuthenticated(APIException): ...          # exception tùy chỉnh
```

### Bảng tổng hợp OOP

| Khái niệm | Nơi áp dụng |
|-----------|-------------|
| Abstract class | `TimestampedModel` |
| Inheritance | 10 model, Permission class, Auth class, ViewSet |
| Override | `get_queryset`, `list/create/destroy`, `has_permission` |
| Encapsulation | 8 service class, `BookingPriceCalculator` |
| Composition | `BookingService` chứa `RoomService` |
| `@property` | `User.is_authenticated`, `BookingService.ten_service` |
| Class constants | `WEEKEND_RATE`, `VIP_DISCOUNT_RATE` |

---

## 3. Hash Mật Khẩu — PBKDF2-SHA256

```python
# hotel_app/services/auth_service.py
from django.contrib.auth.hashers import check_password, make_password

def ma_hoa_mat_khau(mat_khau):
    return make_password(mat_khau)     # PBKDF2-SHA256 + salt ngẫu nhiên

def kiem_tra_mat_khau(user, mat_khau):
    if check_password(mat_khau, user.password):  # so sánh hash an toàn
        return True
    # Tự nâng cấp: plain text cũ → hash lại khi đăng nhập
    if user.password == mat_khau:
        user.password = ma_hoa_mat_khau(mat_khau)
        user.save()
        return True
```

> Mật khẩu **không bao giờ lưu plain text**. Nếu DB cũ có plain text, hệ thống tự động nâng cấp lên hash khi người dùng đăng nhập lần tiếp theo.

---

## 4. Soft Delete Pattern

Không xóa dữ liệu thật — chỉ đánh dấu `is_deleted=True`:

```
DELETE /api/rooms/1/
  → perform_destroy() → room.is_deleted = True (vẫn còn trong DB)

Mọi query bình thường → ActiveManager tự lọc is_deleted=False
Khi cần xem toàn bộ  → AllObjectsManager (không filter)
```

Áp dụng cho **tất cả 10 bảng**: User, Department, Employee, Customer, RoomType, Room, Booking, Invoice, Service, BookingService.

---

## 5. Booking State Machine — Máy Trạng Thái

```
cho_xac_nhan ──xac_nhan()──→ da_xac_nhan ──check_in()──→ dang_o ──check_out()──→ da_tra_phong
      │                           │
      └──────huy()────────────────┘──→ da_huy  (hoàn lại phòng về trạng thái 'trong')
```

Mỗi transition đều kiểm tra trạng thái hiện tại trước khi cho phép chuyển:

```python
# hotel_app/services/booking_service.py
def check_in(self, booking_id):
    if b.status != 'da_xac_nhan':          # guard clause
        return None, msg.BOOKING_MUST_BE_CONFIRMED
    b.status = 'dang_o'
    self._room_service.cap_nhat_trang_thai(b.room_id, 'co_khach')

def huy_booking(self, booking_id):
    if b.status in ['dang_o', 'da_tra_phong']:
        return None, msg.BOOKING_INVALID_CANCEL_STATUS
    b.status = 'da_huy'
    self._room_service.cap_nhat_trang_thai(b.room_id, 'trong')  # hoàn lại phòng
```

---

## 6. Tính Giá Động — Công Thức Phức Hợp

```python
# pricing/services.py
class BookingPriceCalculator:
    WEEKEND_RATE      = Decimal('0.10')   # hằng số class
    VIP_DISCOUNT_RATE = Decimal('0.10')

    def tinh_gia(self, room, check_in, check_out, customer_type):
        base_price   = price_per_night × số_đêm
        weekend_fee  = price_per_night × 10% × số_đêm_cuối_tuần
        vip_discount = (base + weekend_fee) × 10%  # chỉ áp dụng nếu VIP
        final_price  = base_price + weekend_fee - vip_discount

    def _count_weekend_nights(self, check_in, check_out):
        # đếm từng ngày, kiểm tra weekday() in [5, 6] (T7, CN)
```

Có endpoint riêng `/api/pricing/calculate-booking-price/` để tính giá trước khi đặt phòng.

---

## 7. Session-Based Authentication (không dùng JWT/Token)

```python
# hotel_app/authentication.py
class SessionUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = lay_user_hien_tai(request)   # đọc session['user_id']
        if not user:
            return None
        request.hotel_user = user           # gán vào request
        return user, None
```

Session lưu trong **bảng Django sessions trên MySQL** — không dùng cookie JWT hay token header.

---

## 8. Phân Quyền Theo Role (RBAC)

| Role | Quyền |
|------|-------|
| `quan_ly` | Toàn quyền: user, nhân viên, phòng ban, loại phòng, báo cáo |
| `le_tan` | Khách hàng, booking (toàn bộ flow), hóa đơn, dịch vụ |
| Chưa đăng nhập | Chỉ `/register` và `/login` |

```python
# hotel_app/permissions.py
class ManagerOnly(BasePermission):
    def has_permission(self, request, view):
        if user.role != 'quan_ly':
            raise PermissionDenied(msg.AUTH_FORBIDDEN)   # 403
```

---

## 9. Custom Exception Handler — Chuẩn Hóa Lỗi

```python
# core/exceptions.py
def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        # Chuẩn hóa về dạng thống nhất
        response.data = {'error': 'field: message'}
    return response
```

Mọi lỗi từ DRF (400, 401, 403, 404…) đều được format về dạng:

```json
{ "error": "field: message" }
```

---

## 10. Response Envelope Thống Nhất

```python
# core/api.py
def api_response(data=None, message='', status=200, error='', pagination=None):
    body = {}
    if message:    body['message'] = message
    if error:      body['error']   = error
    if data:       body['data']    = data
    if pagination: body['pagination'] = pagination
    return Response(body, status=status)
```

Toàn bộ 77 endpoint trả về cùng một cấu trúc:

```json
{
  "message": "Tạo thành công",
  "data": { "id": 1, "room_number": "101", ... },
  "pagination": {
    "count": 85,
    "next": "http://127.0.0.1:8000/api/rooms/?page=3",
    "previous": "http://127.0.0.1:8000/api/rooms/?page=1"
  }
}
```

---

## 11. Phân Trang — PageNumberPagination

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,   # mặc định 20 bản ghi / trang
}
```

```python
# core/api.py — tích hợp vào response envelope
def paginated_api_response(view, queryset):
    page = view.paginate_queryset(queryset)
    if page is None:
        return api_response(data=...)   # queryset nhỏ, không phân trang

    return api_response(
        data=serializer.data,
        pagination={
            'count':    paginator.page.paginator.count,
            'next':     paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        },
    )
```

Client truyền `?page=2` để lấy trang tiếp theo. Tất cả ViewSet kế thừa `ApiResponseModelViewSet` nên **tự động có phân trang** mà không cần viết thêm.

---

## 12. Rate Limiting — Giới Hạn Request

```python
# config/settings.py
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',   # chưa đăng nhập: 100 request/giờ
    'user': '1000/hour',  # đã đăng nhập: 1000 request/giờ
}
```

---

## 13. Báo Cáo Thống Kê — ORM Aggregation

```python
# hotel_app/services/report_service.py

# Top dịch vụ — dùng annotate + Sum
qs = (BookingService.objects
      .values('service__id', 'service__name', 'service__price')
      .annotate(tong_sl=Sum('quantity'), tong_tien=Sum('subtotal'))
      .order_by('-tong_sl')[:top_n])

# Doanh thu — filter + aggregate
tong = Invoice.objects.filter(payment_status='da_thanh_toan')
              .aggregate(tong=Sum('total'))['tong']
```

| Endpoint | Mô tả |
|----------|-------|
| `GET /api/reports/revenue/` | Doanh thu theo khoảng ngày |
| `GET /api/reports/room-status/` | Tình trạng phòng thời gian thực |
| `GET /api/reports/booking-statistics/` | Thống kê đặt phòng theo trạng thái |
| `GET /api/reports/top-services/?top=N` | Top N dịch vụ sử dụng nhiều nhất |

---

## 14. 35 Serializer — Validation và Nested Data

- Mỗi model phức tạp có **nhiều serializer riêng**: `CreateSerializer`, `UpdateSerializer`, `DetailSerializer`
- Serializer lồng nhau (nested): `BookingSerializer` trả kèm thông tin `Customer`, `Room`, `RoomType`
- Validation nghiệp vụ nằm trong serializer: kiểm tra phòng trống, `check_out > check_in`, unique field

---

## 15. Test Coverage Toàn Diện

| Loại | Chi tiết |
|------|----------|
| Unit tests | ~140 test case, 8 file (model, service, view, permission) |
| E2E toàn bộ 77 endpoint | 1 file ~1.100 dòng, kiểm tra HTTP status + giá trị tính toán |
| E2E booking flow thực tế | 1 file ~765 dòng, kịch bản: tạo → check-in → dịch vụ → check-out → thanh toán |
| Postman collection | 2 scenario đầy đủ (receptionist + manager) |

E2E test kiểm tra:
- HTTP status code chính xác
- Giá trị tính toán (`room_charge`, `service_charge`, `total`)
- Kiểm tra trực tiếp DB sau mỗi bước
- Quyền truy cập (`le_tan` nhận 403 khi gọi endpoint manager)
- Xuất **HTML report** tự động sau khi chạy

```bash
# Chạy unit tests
python manage.py test

# Chạy E2E toàn bộ API
python hotel_app/tests/e2e/full_api/test_e2e_api.py

# Chạy E2E booking flow
python hotel_app/tests/e2e/booking_flow/test_e2e_booking_flow_db.py
```

---

## 16. Localization — Toàn Bộ Tiếng Việt

```python
# core/messages.py — 93 thông báo tập trung
AUTH_REQUIRED            = 'Bạn cần đăng nhập để thực hiện thao tác này.'
AUTH_FORBIDDEN           = 'Bạn không có quyền thực hiện thao tác này.'
BOOKING_ROOM_UNAVAILABLE = 'Phòng không có sẵn trong khoảng thời gian này.'
CHECKOUT_AFTER_CHECKIN   = 'Ngày trả phòng phải sau ngày nhận phòng.'
```

Không hardcode chuỗi trong view hay service — tất cả import từ `core.messages`.

---

## Bảng Tổng Hợp Nhanh

| Tính năng | Kỹ thuật áp dụng |
|-----------|-----------------|
| Kiến trúc | 3 tầng: ViewSet → Service → Model |
| OOP | Kế thừa, override, property, composition, encapsulation |
| Bảo mật mật khẩu | PBKDF2-SHA256 + tự nâng cấp plain text |
| Xóa dữ liệu | Soft Delete + Custom Manager |
| Quy trình đặt phòng | State Machine (5 trạng thái) |
| Tính giá | Công thức: base + phụ thu cuối tuần − giảm giá VIP |
| Đăng nhập | Session-Based (không JWT) |
| Phân quyền | RBAC (quan_ly / le_tan) |
| Lỗi | Custom Exception Handler → format thống nhất |
| Response | API Envelope thống nhất |
| Phân trang | PageNumberPagination, 20 bản ghi/trang |
| Giới hạn request | Rate Limiting (100/h anon, 1000/h user) |
| Thống kê | ORM Aggregation (Sum, annotate, order_by) |
| Serializer | 35 class, nested data, validation nghiệp vụ |
| Test | Unit + E2E + Postman + HTML report |
| Thông báo | 93 message tiếng Việt tập trung |
