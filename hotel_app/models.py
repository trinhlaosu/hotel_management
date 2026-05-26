"""Cac model chinh cua he thong quan ly khach san."""
from django.db import models


# Abstract Base Model cho timestamp
class TimestampedModel(models.Model):
    """Abstract model for timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True


# Custom Manager cho soft delete
class ActiveManager(models.Manager):
    """Manager that filters out soft-deleted objects."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Manager that returns all objects including soft-deleted."""
    pass


# Bang 1: Tai khoan
class User(TimestampedModel):
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

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'User'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return str([self.id, self.username, self.role])

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


# Bang 2: Phong ban
class Department(TimestampedModel):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Department'
        ordering = ['name']

    def __str__(self):
        return str([self.id, self.name])


# Bang 3: Nhan vien
class Employee(TimestampedModel):
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
                                      default=0)        # VND
    hire_date   = models.DateField()
    shift       = models.CharField(max_length=20, choices=SHIFT_CHOICES,
                                   default='sang')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                   default='dang_lam')

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Employee'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['department', 'status']),
        ]

    def __str__(self):
        return str([self.id, self.full_name, self.get_shift_display()])


# Bang 4: Khach hang
class Customer(TimestampedModel):
    CUSTOMER_TYPE_CHOICES = [
        ('regular', 'Thường'),
        ('vip',     'VIP'),
    ]

    full_name     = models.CharField(max_length=100)
    phone         = models.CharField(max_length=15, unique=True)
    email         = models.EmailField(blank=True, null=True)
    id_card       = models.CharField(max_length=20, unique=True)  # CCCD
    address       = models.TextField(blank=True, null=True)
    customer_type = models.CharField(max_length=20,
                                     choices=CUSTOMER_TYPE_CHOICES,
                                     default='regular')

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Customer'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['id_card']),
        ]

    def __str__(self):
        return str([self.id, self.full_name, self.customer_type])


# Bang 5: Loai phong
class RoomType(TimestampedModel):
    name            = models.CharField(max_length=50, unique=True)
    price_per_night = models.DecimalField(max_digits=15, decimal_places=0)
    capacity        = models.IntegerField(default=2)
    description     = models.TextField(blank=True, null=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'RoomType'
        ordering = ['name']

    def __str__(self):
        return str([self.id, self.name, float(self.price_per_night)])


# Bang 6: Phong
class Room(TimestampedModel):
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

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Room'
        ordering = ['floor', 'room_number']
        indexes = [
            models.Index(fields=['room_type', 'status']),
        ]

    def __str__(self):
        return str([self.id, self.room_number, self.status])


# Bang 7: Dat phong
class Booking(TimestampedModel):
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

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Booking'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['room', 'check_in', 'check_out']),
        ]

    def __str__(self):
        return str([self.id, self.customer_id, self.room_id, self.status])


# Bang 8: Hoa don
class Invoice(TimestampedModel):
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
                                         default=0)   # Tien phong
    service_charge = models.DecimalField(max_digits=15, decimal_places=0,
                                         default=0)   # Tien dich vu
    total          = models.DecimalField(max_digits=15, decimal_places=0,
                                         default=0)   # Tong tien
    payment_status = models.CharField(max_length=20,
                                      choices=PAYMENT_STATUS_CHOICES,
                                      default='chua_thanh_toan')
    payment_method = models.CharField(max_length=20,
                                      choices=PAYMENT_METHOD_CHOICES,
                                      null=True, blank=True)
    paid_at        = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Invoice'
        ordering = ['-created_at']

    def __str__(self):
        return str([self.id, self.booking_id, float(self.total),
                    self.payment_status])


# Bang 9: Dich vu
class Service(TimestampedModel):
    name        = models.CharField(max_length=100, unique=True)
    price       = models.DecimalField(max_digits=15, decimal_places=0)
    description = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'Service'
        ordering = ['name']

    def __str__(self):
        return str([self.id, self.name, float(self.price)])


# Bang 10: Dich vu theo booking
class BookingService(TimestampedModel):
    booking  = models.ForeignKey(Booking, on_delete=models.CASCADE,
                                 related_name='booking_services')
    service  = models.ForeignKey(Service, on_delete=models.RESTRICT,
                                 related_name='booking_services')
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=15, decimal_places=0,
                                   default=0)   # quantity x price

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        db_table = 'BookingService'
        ordering = ['-created_at']

    def __str__(self):
        return str([self.id, self.booking_id, self.service_id,
                    self.quantity, float(self.subtotal)])

