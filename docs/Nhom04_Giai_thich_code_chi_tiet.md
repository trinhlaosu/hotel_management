# Giải Thích Code Chi Tiết Theo Luồng

Tài liệu này giải thích code theo hướng gần với từng dòng/nhóm dòng quan trọng. Mục tiêu là giúp nhóm có thể trình bày được khi được hỏi: request đi từ đâu, file nào xử lý, dòng code đó làm gì và vì sao cần có.

## 1. Luồng Tổng Quát Khi Gọi API

Ví dụ gọi API:

```text
POST /api/bookings/
```

Luồng xử lý:

```text
config/urls.py
-> hotel_app/urls.py
-> hotel_app/views/bookings.py
-> hotel_app/serializers/bookings.py
-> hotel_app/services/booking_service.py
-> hotel_app/services/invoice_service.py
-> hotel_app/models.py
-> core/api.py
```

Ý nghĩa:

```text
URL định tuyến request
ViewSet nhận request
Serializer kiểm tra dữ liệu đầu vào
Service xử lý nghiệp vụ
Model thao tác database
Core chuẩn hóa response JSON
```

## 2. `manage.py`

File `manage.py` là điểm chạy lệnh Django.

```python
import os
import sys
```

Hai dòng này import thư viện hệ thống. `os` dùng để set biến môi trường, `sys` dùng để đọc tham số lệnh.

```python
def main():
```

Định nghĩa hàm chính khi chạy project.

```python
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

Khai báo file cấu hình mặc định của Django là `config/settings.py`.

```python
    from django.core.management import execute_from_command_line
```

Import hàm xử lý command của Django, ví dụ `runserver`, `test`, `migrate`.

```python
    execute_from_command_line(sys.argv)
```

Chạy lệnh Django dựa trên tham số người dùng nhập ở terminal.

```python
if __name__ == '__main__':
    main()
```

Nếu chạy trực tiếp `python manage.py ...` thì gọi hàm `main()`.

## 3. `config/settings.py`

File này cấu hình toàn bộ project.

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

Xác định thư mục gốc của project.

```python
SECRET_KEY = '...'
DEBUG = True
ALLOWED_HOSTS = ['*']
```

`SECRET_KEY` dùng nội bộ cho bảo mật Django. `DEBUG=True` phù hợp môi trường học/demo. `ALLOWED_HOSTS=['*']` cho phép truy cập từ mọi host khi chạy thử.

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'hotel_app.apps.HotelConfig',
]
```

Khai báo các app được Django sử dụng.

- `rest_framework`: dùng Django REST Framework.
- `django_filters`: hỗ trợ lọc dữ liệu API.
- `hotel_app.apps.HotelConfig`: app chính của project.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hotel_management',
        ...
    }
}
```

Cấu hình kết nối MySQL. Project dùng database tên `hotel_management`.

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

Session đăng nhập được lưu trong database.

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'hotel_app.authentication.SessionUserAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'hotel_app.permissions.SessionAuthenticated',
    ],
    ...
}
```

Cấu hình mặc định cho DRF:

- Dùng authentication custom dựa trên session.
- Mặc định API yêu cầu đăng nhập.
- Có pagination.
- Có filter/search/order.
- Có exception handler riêng để lỗi trả về dạng thống nhất.

## 4. `config/urls.py`

File này là URL gốc của project.

```python
from django.contrib import admin
from django.urls import include, path
```

Import admin và hàm định tuyến URL.

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('hotel_app.urls')),
]
```

Ý nghĩa:

- `/admin/` đi vào Django admin.
- `/api/` chuyển tiếp sang `hotel_app/urls.py`.

## 5. `hotel_app/urls.py`

File này đăng ký toàn bộ API bằng DRF router.

```python
router = DefaultRouter(trailing_slash=True)
```

Tạo router tự động sinh URL REST. `trailing_slash=True` nghĩa là endpoint có dấu `/` cuối.

```python
router.register('auth', AuthViewSet, basename='auth')
```

Đăng ký nhóm API auth. Ví dụ:

```text
/api/auth/login/
/api/auth/register/
```

```python
router.register('bookings', BookingViewSet, basename='bookings')
```

Đăng ký nhóm booking. Router tự sinh:

```text
GET    /api/bookings/
POST   /api/bookings/
GET    /api/bookings/<id>/
PUT    /api/bookings/<id>/
DELETE /api/bookings/<id>/
```

Các `@action` trong ViewSet sẽ sinh thêm endpoint custom như:

```text
/api/bookings/<id>/confirm/
/api/bookings/<id>/check-in/
```

```python
urlpatterns = [
    path('', include(router.urls)),
]
```

Gắn toàn bộ URL router vào app.

## 6. `hotel_app/models.py`

File này định nghĩa bảng database.

### 6.1. `TimestampedModel`

```python
class TimestampedModel(models.Model):
```

Định nghĩa model cha dùng chung.

```python
created_at = models.DateTimeField(auto_now_add=True)
```

Tự động lưu thời điểm tạo bản ghi.

```python
updated_at = models.DateTimeField(auto_now=True)
```

Tự động cập nhật thời điểm sửa bản ghi.

```python
is_deleted = models.BooleanField(default=False, db_index=True)
```

Dùng cho soft delete. Khi xóa, bản ghi không mất khỏi database mà chỉ đánh dấu `is_deleted=True`.

```python
class Meta:
    abstract = True
```

Model này chỉ làm lớp cha, không tạo bảng riêng.

### 6.2. `ActiveManager`

```python
class ActiveManager(models.Manager):
```

Tạo manager riêng.

```python
def get_queryset(self):
    return super().get_queryset().filter(is_deleted=False)
```

Mặc định chỉ lấy dữ liệu chưa bị xóa mềm.

### 6.3. `User`

```python
class User(TimestampedModel):
```

Model tài khoản kế thừa timestamp và soft delete.

```python
username = models.CharField(max_length=50, unique=True)
password = models.CharField(max_length=255)
email = models.EmailField(unique=True)
```

Lưu username, password hash và email.

```python
role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='le_tan')
```

Vai trò người dùng, gồm `quan_ly` và `le_tan`.

```python
is_active = models.BooleanField(default=True)
```

Cho biết tài khoản có được đăng nhập hay không.

```python
objects = ActiveManager()
all_objects = AllObjectsManager()
```

`objects` chỉ lấy bản ghi chưa bị soft delete. `all_objects` lấy tất cả.

### 6.4. Các model nghiệp vụ chính

```text
Department       phòng ban
Employee         nhân viên
Customer         khách hàng
RoomType         loại phòng
Room             phòng cụ thể
Booking          đặt phòng
Invoice          hóa đơn
Service          dịch vụ
BookingService   dịch vụ dùng trong booking
```

Các model này đều kế thừa `TimestampedModel`, nên đều có:

```text
created_at
updated_at
is_deleted
```

## 7. Auth Flow Chi Tiết

### 7.1. `hotel_app/views/auth.py`

```python
class AuthViewSet(viewsets.ViewSet):
```

Tạo ViewSet xử lý nhóm API auth.

```python
def get_permissions(self):
```

Hàm quyết định API nào cần đăng nhập.

```python
if self.action in ['profile', 'change_password']:
    return [SessionAuthenticated()]
return []
```

`profile` và `change_password` cần đăng nhập. `register`, `login`, `logout` không bắt buộc.

### 7.2. Register

```python
@action(detail=False, methods=['post'])
def register(self, request):
```

Tạo endpoint:

```text
POST /api/auth/register/
```

```python
serializer = RegisterSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
```

Đưa dữ liệu request vào serializer để validate. Nếu sai thì tự trả lỗi.

```python
user, err_msg = svc.dang_ky(serializer.validated_data)
```

Gọi `AuthService` để tạo tài khoản.

```python
if not user:
    return Response({'error': err_msg}, status=400)
```

Nếu không tạo được user thì trả lỗi.

```python
return Response({...}, status=201)
```

Tạo thành công thì trả status 201.

### 7.3. Login

```python
serializer = LoginSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
```

Validate username và password.

```python
user, err_msg = AuthService().dang_nhap(...)
```

Gọi service để kiểm tra tài khoản.

```python
request.session['user_id'] = user.id
request.session['role'] = user.role
```

Lưu thông tin đăng nhập vào session.

```python
return Response({'message': ..., 'data': ...}, status=200)
```

Trả thông tin user sau khi đăng nhập.

### 7.4. `hotel_app/services/auth_service.py`

```python
def ma_hoa_mat_khau(mat_khau):
    return make_password(mat_khau)
```

Hash mật khẩu trước khi lưu database.

```python
def kiem_tra_mat_khau(user, mat_khau):
```

Kiểm tra mật khẩu người dùng nhập.

```python
if check_password(mat_khau, user.password):
    return True
```

So sánh mật khẩu nhập với password hash.

```python
if user.password == mat_khau:
    user.password = ma_hoa_mat_khau(mat_khau)
    user.save(update_fields=['password'])
    return True
```

Hỗ trợ tài khoản cũ đang lưu plain text: nếu đúng thì tự hash lại.

```python
def dang_nhap(self, username, password):
```

Xử lý đăng nhập.

```python
user = User.objects.get(username=username, is_active=True)
```

Chỉ cho đăng nhập nếu tài khoản active.

```python
if not kiem_tra_mat_khau(user, password):
    return None, msg.AUTH_INVALID_CREDENTIALS
```

Sai mật khẩu thì trả lỗi.

## 8. Booking Flow Chi Tiết

### 8.1. `hotel_app/views/bookings.py`

```python
class BookingViewSet(viewsets.GenericViewSet):
```

ViewSet xử lý booking. Dùng `GenericViewSet` vì nhiều action được viết custom.

```python
queryset = Booking.objects.select_related('customer', 'room', 'room__room_type')
```

Khi lấy booking thì lấy kèm customer, room và room type để giảm số query.

```python
permission_classes = [SessionAuthenticated]
```

Mọi API booking đều yêu cầu đăng nhập.

```python
def get_serializer_class(self):
```

Chọn serializer theo action.

```python
if self.action == 'create':
    return BookingCreateSerializer
```

Khi tạo booking dùng serializer riêng cho create.

```python
if self.action in ['update', 'partial_update']:
    return BookingUpdateSerializer
```

Khi update chỉ cho cập nhật note.

```python
if self.action == 'services':
    return BookingServiceCreateSerializer
```

Khi thêm dịch vụ vào booking thì dùng serializer dịch vụ.

### 8.2. Tạo booking

```python
def create(self, request):
```

Xử lý:

```text
POST /api/bookings/
```

```python
serializer = self.get_serializer(data=request.data)
```

Lấy serializer phù hợp với action create.

```python
if not serializer.is_valid():
    return serializer_error_response(serializer)
```

Nếu dữ liệu không hợp lệ thì trả lỗi dạng thống nhất.

```python
booking, invoice, err_msg = self.get_booking_service().tao_booking_va_hoa_don(
    request.hotel_user,
    serializer.validated_data,
)
```

Gọi service tạo booking và hóa đơn ban đầu.

```python
if not booking:
    return api_response(error=err_msg, status=400)
```

Nếu booking không tạo được thì trả lỗi.

```python
return api_response(..., status=201)
```

Tạo thành công thì trả status 201.

### 8.3. `BookingCreateSerializer`

```python
customer_id = NotFoundPrimaryKeyRelatedField(
    source='customer',
    queryset=Customer.objects.all(),
    write_only=True,
)
```

Input nhận `customer_id`, nhưng serializer chuyển thành object `customer`.

```python
room_id = NotFoundPrimaryKeyRelatedField(...)
```

Tương tự, nhận `room_id`, chuyển thành object `room`.

```python
if data['check_out'] <= data['check_in']:
    raise serializers.ValidationError(...)
```

Kiểm tra ngày trả phòng phải sau ngày nhận phòng.

```python
existing = Booking.objects.filter(
    room=data['room'],
    status__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_o'],
).exclude(is_deleted=True)
```

Tìm booking đang giữ phòng trong các trạng thái còn hiệu lực.

```python
if existing.filter(
    check_in__lt=data['check_out'],
    check_out__gt=data['check_in'],
).exists():
```

Kiểm tra có bị trùng khoảng ngày hay không.

```python
raise serializers.ValidationError({'room': msg.BOOKING_ROOM_UNAVAILABLE})
```

Nếu trùng thì báo phòng không khả dụng.

### 8.4. `hotel_app/services/booking_service.py`

```python
def tao_booking_va_hoa_don(self, user, data):
```

Hàm nghiệp vụ chính khi tạo booking.

```python
try:
    employee = Employee.objects.get(user=user)
    data['created_by_id'] = employee.id
except Employee.DoesNotExist:
    data['created_by_id'] = None
```

Nếu user có hồ sơ nhân viên thì lưu nhân viên tạo booking. Nếu không có thì để null.

```python
booking, err_msg = self.tao_booking(data)
```

Gọi hàm tạo booking.

```python
if not booking:
    return None, None, err_msg
```

Nếu tạo booking thất bại thì trả lỗi.

```python
booking_full = Booking.objects.select_related(
    'room', 'room__room_type'
).get(id=booking.id)
```

Lấy lại booking kèm thông tin phòng và loại phòng để tính tiền.

```python
invoice = InvoiceService().tao_hoa_don(booking_full)
```

Tạo hóa đơn ban đầu cho booking.

```python
return booking, invoice, None
```

Trả booking và invoice về view.

### 8.5. Confirm, check-in, check-out

```python
def xac_nhan_booking(self, booking_id):
```

Chuyển booking từ `cho_xac_nhan` sang `da_xac_nhan`.

```python
if b.status != 'cho_xac_nhan':
    return None, msg.BOOKING_INVALID_CONFIRM_STATUS.format(status=b.status)
```

Chỉ booking đang chờ xác nhận mới được confirm.

```python
b.status = 'da_xac_nhan'
b.save()
```

Cập nhật trạng thái.

```python
def check_in(self, booking_id):
```

Check-in booking.

```python
if b.status != 'da_xac_nhan':
    return None, msg.BOOKING_MUST_BE_CONFIRMED
```

Booking phải được xác nhận trước khi check-in.

```python
b.status = 'dang_o'
self._room_service.cap_nhat_trang_thai(b.room_id, 'co_khach')
```

Booking chuyển sang đang ở, phòng chuyển sang có khách.

```python
def check_out(self, booking_id):
```

Check-out booking.

```python
if b.status != 'dang_o':
    return None, msg.BOOKING_NOT_CHECKED_IN
```

Chỉ booking đang ở mới được check-out.

```python
b.status = 'da_tra_phong'
self._room_service.cap_nhat_trang_thai(b.room_id, 'trong')
```

Booking đã trả phòng, phòng trở lại trống.

```python
inv_svc.cap_nhat_hoa_don(b)
```

Cập nhật hóa đơn lần cuối.

## 9. Booking Service Và Hóa Đơn Chi Tiết

### 9.1. `hotel_app/services/service_service.py`

```python
def them_dich_vu_cho_booking(self, booking_id, data):
```

Thêm dịch vụ vào booking.

```python
booking = Booking.objects.select_related('room', 'room__room_type').get(id=booking_id)
```

Kiểm tra booking tồn tại và lấy kèm phòng để tính hóa đơn.

```python
except Booking.DoesNotExist:
    return None, msg.BOOKING_NOT_FOUND, 404
```

Nếu booking không tồn tại thì trả 404.

```python
service_id = data.get('service_id') or _model_id(data.get('service'))
```

Lấy ID dịch vụ từ input.

```python
service = Service.objects.get(id=service_id)
```

Tìm dịch vụ.

```python
quantity, err = self._parse_quantity(data.get('quantity'))
```

Kiểm tra số lượng hợp lệ.

```python
booking_service = BookingServiceModel.objects.create(
    booking_id=booking_id,
    service=service,
    quantity=quantity,
    subtotal=float(service.price) * quantity,
)
```

Tạo dòng dịch vụ đã dùng và tính thành tiền.

```python
InvoiceService().cap_nhat_hoa_don(booking)
```

Cập nhật lại hóa đơn sau khi thêm dịch vụ.

### 9.2. Cập nhật dịch vụ trong booking

```python
booking_service = BookingServiceModel.objects.select_related('service').get(id=booking_service_id)
```

Lấy dòng dịch vụ kèm thông tin dịch vụ.

```python
quantity, err = self._parse_quantity(data.get('quantity', booking_service.quantity))
```

Nếu request có quantity mới thì lấy quantity mới; nếu không thì giữ quantity cũ.

```python
booking_service.subtotal = float(booking_service.service.price) * quantity
```

Tính lại thành tiền.

```python
InvoiceService().cap_nhat_hoa_don(booking)
```

Cập nhật hóa đơn sau khi sửa dịch vụ.

### 9.3. Xóa dịch vụ trong booking

```python
booking_service = BookingServiceModel.objects.get(id=booking_service_id)
```

Tìm dòng dịch vụ cần xóa.

```python
booking = Booking.objects.select_related(...).get(id=booking_service.booking_id)
```

Lưu lại booking trước khi xóa để còn cập nhật hóa đơn.

```python
booking_service.delete()
```

Xóa dòng dịch vụ.

```python
InvoiceService().cap_nhat_hoa_don(booking)
```

Cập nhật lại hóa đơn sau khi xóa.

## 10. Invoice Service Chi Tiết

File:

```text
hotel_app/services/invoice_service.py
```

```python
def __tinh_tien(self, booking):
```

Hàm private dùng để tính tiền phòng và tiền dịch vụ.

```python
so_dem = (co - ci).days
```

Tính số đêm ở.

```python
gia_dem = float(booking.room.room_type.price_per_night)
tien_phong = so_dem * gia_dem
```

Tính tiền phòng.

```python
ds_dv = BookingService.objects.filter(booking_id=booking.id)
tien_dv = sum(float(dv.subtotal) for dv in ds_dv)
```

Tính tổng tiền dịch vụ.

```python
return tien_phong, tien_dv
```

Trả về tiền phòng và tiền dịch vụ.

```python
def tao_hoa_don(self, booking):
```

Tạo hóa đơn ban đầu.

```python
invoice, _ = Invoice.objects.get_or_create(...)
```

Nếu booking chưa có hóa đơn thì tạo mới, nếu có rồi thì lấy hóa đơn cũ.

```python
def cap_nhat_hoa_don(self, booking):
```

Cập nhật lại hóa đơn sau khi dịch vụ thay đổi hoặc check-out.

```python
inv.room_charge = tien_phong
inv.service_charge = tien_dv
inv.total = tong
inv.save()
```

Lưu lại tiền phòng, tiền dịch vụ và tổng tiền.

```python
def thanh_toan(self, invoice_id, phuong_thuc):
```

Thanh toán hóa đơn.

```python
if inv.payment_status == 'da_thanh_toan':
    return None, msg.INVOICE_ALREADY_PAID
```

Không cho thanh toán lại hóa đơn đã thanh toán.

```python
inv.payment_status = 'da_thanh_toan'
inv.payment_method = phuong_thuc
inv.paid_at = timezone.now()
inv.save()
```

Cập nhật trạng thái thanh toán.

## 11. Core Response Chi Tiết

File:

```text
core/api.py
```

```python
def api_response(data=None, message='', status=200, error='', pagination=None):
```

Hàm chuẩn hóa response JSON.

```python
body = {}
```

Tạo object response rỗng.

```python
if message:
    body['message'] = message
```

Nếu có message thì thêm vào response.

```python
if error:
    body['error'] = error
```

Nếu có lỗi thì thêm `error`.

```python
if data is not None:
    body['data'] = data
```

Nếu có dữ liệu thì thêm `data`.

```python
return Response(body, status=status)
```

Trả response cho client.

```python
class ApiResponseModelViewSet(viewsets.ModelViewSet):
```

Lớp cha dùng chung cho các CRUD API.

```python
def list(self, request, *args, **kwargs):
```

Xử lý GET danh sách.

```python
def create(self, request, *args, **kwargs):
```

Xử lý POST tạo mới.

```python
def update(self, request, *args, **kwargs):
```

Xử lý PUT cập nhật.

```python
def destroy(self, request, *args, **kwargs):
```

Xử lý DELETE.

```python
def perform_destroy(self, instance):
    if hasattr(instance, 'is_deleted'):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])
        return
    super().perform_destroy(instance)
```

Nếu model có `is_deleted` thì soft delete, không xóa khỏi database. Nếu model không có `is_deleted` thì dùng delete mặc định.

## 12. E2E Test Chi Tiết

File:

```text
hotel_app/tests/e2e/test_e2e_booking_flow.py
```

```python
class BookingFlowE2ETest(BaseTest):
```

Tạo class test luồng end-to-end.

```python
def test_e2e_booking_service_invoice_payment_report_flow(self):
```

Một test kiểm tra toàn bộ luồng nghiệp vụ chính.

```python
login_res = self.login("nv_chuyen")
```

Đăng nhập bằng tài khoản lễ tân.

```python
rooms_res = self.client.get("/api/rooms/?status=trong")
```

Xem phòng trống.

```python
customer_res = self.post("/api/customers/", {...})
```

Tạo khách hàng mới.

```python
booking_res = self.post("/api/bookings/", {...})
```

Tạo booking.

```python
confirm_res = self.put(f"/api/bookings/{booking_id}/confirm/")
```

Xác nhận booking.

```python
check_in_res = self.put(f"/api/bookings/{booking_id}/check-in/")
```

Check-in.

```python
service_res = self.post(f"/api/bookings/{booking_id}/services/", {...})
```

Thêm dịch vụ vào booking.

```python
invoice = Invoice.objects.get(booking_id=booking_id)
```

Kiểm tra hóa đơn trong database đã cập nhật.

```python
check_out_res = self.put(f"/api/bookings/{booking_id}/check-out/")
```

Check-out.

```python
pay_res = self.put(f"/api/invoices/{invoice_id}/pay/", {...})
```

Thanh toán hóa đơn.

```python
admin_login_res = self.login("admin_mychi")
```

Đăng nhập quản lý để xem báo cáo.

```python
revenue_res = self.client.get("/api/reports/revenue/")
```

Kiểm tra báo cáo doanh thu.

## 13. Cách Trình Bày Khi Được Hỏi Code

Nếu thầy hỏi “một request chạy qua những file nào?”, trả lời:

```text
Request đi từ config/urls.py sang hotel_app/urls.py.
Router chuyển request vào ViewSet tương ứng trong hotel_app/views.
ViewSet chọn serializer để validate dữ liệu.
Sau đó ViewSet gọi service để xử lý nghiệp vụ.
Service thao tác với model trong hotel_app/models.py.
Kết quả được trả về bằng api_response trong core/api.py.
```

Nếu thầy hỏi “vì sao có service layer?”, trả lời:

```text
Service layer giúp tách nghiệp vụ khỏi view.
View chỉ nhận request và trả response.
Các xử lý như tạo booking, cập nhật phòng, tính hóa đơn, thanh toán được đặt trong service để code dễ đọc và dễ test hơn.
```

Nếu thầy hỏi “vì sao có serializer?”, trả lời:

```text
Serializer dùng để kiểm tra dữ liệu đầu vào, chuyển ID thành object model và format dữ liệu trả về JSON.
Nhờ serializer, view không phải tự kiểm tra từng field thủ công.
```

Nếu thầy hỏi “soft delete là gì?”, trả lời:

```text
Soft delete là không xóa dữ liệu khỏi database mà chỉ đánh dấu is_deleted=True.
Điều này giúp giữ lịch sử dữ liệu, đặc biệt với khách hàng, phòng, phòng ban hoặc loại phòng đã từng phát sinh booking.
```
