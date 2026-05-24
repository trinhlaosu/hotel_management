"""
Models – 10 bảng CSDL cho hệ thống Quản lý Khách sạn (nội bộ)
Áp dụng: Lập trình hướng đối tượng (kế thừa django.db.models.Model)
"""
from django.db import models


# ------------------------------------------------------------------ #
#  BẢNG 1: User – Tài khoản nội bộ (Quản lý / Lễ tân)               #
# ------------------------------------------------------------------ #
class User(models.Model):
    ROLE_CHOICES = [
        ('quan_ly', 'Quản lý'),
        ('le_tan',  'Lễ tân / Nhân viên'),
    ]

    username   = models.CharField(max_length=50, unique=True)
    password   = models.CharField(max_length=255)
    email      = models.EmailField(unique=True)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES,
                                  default='le_tan')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'User'

    def __str__(self):
        return str([self.id, self.username, self.role])


# ------------------------------------------------------------------ #
#  BẢNG 2: Department – Phòng ban                                     #
# ------------------------------------------------------------------ #
class Department(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Department'

    def __str__(self):
        return str([self.id, self.name])


# ------------------------------------------------------------------ #
#  BẢNG 3: Employee – Hồ sơ nhân viên                                #
# ------------------------------------------------------------------ #
class Employee(models.Model):
    SHIFT_CHOICES = [
        ('sang',  'Ca sáng'),
        ('chieu', 'Ca chiều'),
        ('toi',   'Ca tối'),
    ]
    STATUS_CHOICES = [
        ('dang_lam',  'Đang làm'),
        ('nghi_viec', 'Nghỉ việc'),
    ]

    user        = models.OneToOneField(User,       on_delete=models.CASCADE,
                                       related_name='employee')
    department  = models.ForeignKey(Department,    on_delete=models.RESTRICT,
                                       related_name='employees')
    full_name   = models.CharField(max_length=100)
    phone       = models.CharField(max_length=15)
    salary      = models.DecimalField(max_digits=15, decimal_places=0,
                                      default=0)        # Đơn vị: VNĐ
    hire_date   = models.DateField()
    shift       = models.CharField(max_length=20, choices=SHIFT_CHOICES,
                                   default='sang')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                   default='dang_lam')

    class Meta:
        db_table = 'Employee'

    def __str__(self):
        return str([self.id, self.full_name, self.get_shift_display()])


# ------------------------------------------------------------------ #
#  BẢNG 4: Customer – Khách hàng (do nhân viên nhập)                 #
# ------------------------------------------------------------------ #
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('regular', 'Thường'),
        ('vip',     'VIP'),
    ]

    full_name     = models.CharField(max_length=100)
    phone         = models.CharField(max_length=15, unique=True)
    email         = models.EmailField(blank=True, null=True)
    id_card       = models.CharField(max_length=20, unique=True)  # Số CCCD
    address       = models.TextField(blank=True, null=True)
    customer_type = models.CharField(max_length=20,
                                     choices=CUSTOMER_TYPE_CHOICES,
                                     default='regular')

    class Meta:
        db_table = 'Customer'

    def __str__(self):
        return str([self.id, self.full_name, self.customer_type])


# ------------------------------------------------------------------ #
#  BẢNG 5: RoomType – Loại phòng                                      #
# ------------------------------------------------------------------ #
class RoomType(models.Model):
    name            = models.CharField(max_length=50, unique=True)
    price_per_night = models.DecimalField(max_digits=15, decimal_places=0)
                                                         # Đơn vị: VNĐ
    capacity        = models.IntegerField(default=2)
    description     = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'RoomType'

    def __str__(self):
        return str([self.id, self.name, float(self.price_per_night)])


# ------------------------------------------------------------------ #
#  BẢNG 6: Room – Phòng khách sạn                                     #
# ------------------------------------------------------------------ #
class Room(models.Model):
    STATUS_CHOICES = [
        ('trong',    'Còn trống'),
        ('co_khach', 'Có khách'),
        ('bao_tri',  'Bảo trì'),
    ]

    room_type   = models.ForeignKey(RoomType, on_delete=models.RESTRICT,
                                    related_name='rooms')
    room_number = models.CharField(max_length=10, unique=True)
    floor       = models.IntegerField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                   default='trong')

    class Meta:
        db_table = 'Room'

    def __str__(self):
        return str([self.id, self.room_number, self.status])


# ------------------------------------------------------------------ #
#  BẢNG 7: Booking – Đặt phòng                                        #
# ------------------------------------------------------------------ #
class Booking(models.Model):
    STATUS_CHOICES = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan',  'Đã xác nhận'),
        ('dang_o',       'Đang ở'),
        ('da_tra_phong', 'Đã trả phòng'),
        ('da_huy',       'Đã hủy'),
    ]

    customer   = models.ForeignKey(Customer, on_delete=models.RESTRICT,
                                   related_name='bookings')
    room       = models.ForeignKey(Room,     on_delete=models.RESTRICT,
                                   related_name='bookings')
    check_in   = models.DateField()
    check_out  = models.DateField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                  default='cho_xac_nhan')
    note       = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='created_bookings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Booking'

    def __str__(self):
        return str([self.id, self.customer_id, self.room_id, self.status])


# ------------------------------------------------------------------ #
#  BẢNG 8: Invoice – Hóa đơn                                          #
# ------------------------------------------------------------------ #
class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('chua_thanh_toan', 'Chưa thanh toán'),
        ('da_thanh_toan',   'Đã thanh toán'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('tien_mat',     'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the',          'Thẻ'),
    ]

    booking        = models.OneToOneField(Booking, on_delete=models.CASCADE,
                                          related_name='invoice')
    room_charge    = models.DecimalField(max_digits=15, decimal_places=0,
                                         default=0)   # Tiền phòng (VNĐ)
    service_charge = models.DecimalField(max_digits=15, decimal_places=0,
                                         default=0)   # Tiền dịch vụ (VNĐ)
    total          = models.DecimalField(max_digits=15, decimal_places=0,
                                         default=0)   # Tổng tiền (VNĐ)
    payment_status = models.CharField(max_length=20,
                                      choices=PAYMENT_STATUS_CHOICES,
                                      default='chua_thanh_toan')
    payment_method = models.CharField(max_length=20,
                                      choices=PAYMENT_METHOD_CHOICES,
                                      null=True, blank=True)
    paid_at        = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Invoice'

    def __str__(self):
        return str([self.id, self.booking_id, float(self.total),
                    self.payment_status])


# ------------------------------------------------------------------ #
#  BẢNG 9: Service – Dịch vụ                                          #
# ------------------------------------------------------------------ #
class Service(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    price       = models.DecimalField(max_digits=15, decimal_places=0)
                                                      # Đơn vị: VNĐ
    description = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'Service'

    def __str__(self):
        return str([self.id, self.name, float(self.price)])


# ------------------------------------------------------------------ #
#  BẢNG 10: BookingService – Dịch vụ sử dụng theo booking            #
# ------------------------------------------------------------------ #
class BookingService(models.Model):
    booking  = models.ForeignKey(Booking, on_delete=models.CASCADE,
                                 related_name='booking_services')
    service  = models.ForeignKey(Service, on_delete=models.RESTRICT,
                                 related_name='booking_services')
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=15, decimal_places=0,
                                   default=0)   # quantity x price (VNĐ)
    used_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'BookingService'

    def __str__(self):
        return str([self.id, self.booking_id, self.service_id,
                    self.quantity, float(self.subtotal)])

