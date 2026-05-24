"""
Views – 28 chức năng Web API Quản lý Khách sạn (nội bộ)
Phong cách: Class-Based Views theo hướng dẫn thầy (buổi 09)
Áp dụng: @csrf_exempt, JsonResponse, OOP Services
"""
import json
from django.contrib.auth.hashers import check_password, make_password
from django.http    import JsonResponse
from django.views   import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils   import timezone

from hotel.models   import (User, Department, Employee, Customer,
                             RoomType, Room, Booking, Invoice,
                             Service, BookingService as BookingServiceModel)
from hotel.services.room_service    import RoomService
from hotel.services.booking_service import BookingService as BookingWorkflowService
from hotel.services.invoice_service import InvoiceService
from hotel.services.report_service  import ReportService
from core.utils      import phan_hoi, doc_json, kiem_tra_role, yeu_cau_dang_nhap
from core.validators import kiem_tra_truong_bat_buoc, kiem_tra_ngay


def ma_hoa_mat_khau(mat_khau):
    return make_password(mat_khau)


def kiem_tra_mat_khau(user, mat_khau):
    if not mat_khau:
        return False
    if check_password(mat_khau, user.password):
        return True
    if user.password == mat_khau:
        user.password = ma_hoa_mat_khau(mat_khau)
        user.save(update_fields=['password'])
        return True
    return False


# ================================================================== #
#  1. AUTH – Đăng nhập / Đăng xuất / Hồ sơ                          #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class AuthView(View):

    def post(self, request):
        """POST /api/auth/login/ | POST /api/auth/logout/"""
        path = request.path

        # ── Đăng nhập ──
        if path.endswith('/register/'):
            data, err = doc_json(request)
            if err:
                return err

            ok, msg = kiem_tra_truong_bat_buoc(data,
                  ['username', 'password', 'email'])
            if not ok:
                return phan_hoi(error=msg, status=400)

            if User.objects.filter(username=data['username']).exists():
                return phan_hoi(error='Username da ton tai', status=400)
            if User.objects.filter(email=data['email']).exists():
                return phan_hoi(error='Email da ton tai', status=400)

            user = User.objects.create(
                username=data['username'],
                password=ma_hoa_mat_khau(data['password']),
                email=data['email'],
                role='le_tan',
                is_active=False)
            return phan_hoi(
                data={'user_id': user.id, 'username': user.username,
                      'role': user.role, 'is_active': user.is_active},
                message='Dang ky thanh cong, vui long cho quan ly duyet',
                status=201)

        if path.endswith('/login/'):
            data, err = doc_json(request)
            if err:
                return err
            username = data.get('username')
            password = data.get('password')
            try:
                user = User.objects.get(username=username, is_active=True)
            except User.DoesNotExist:
                return phan_hoi(error='Sai username hoặc mật khẩu', status=400)
            if not kiem_tra_mat_khau(user, password):
                return phan_hoi(error='Sai username hoặc mật khẩu', status=400)

            # Lưu session
            request.session['user_id'] = user.id
            request.session['role']    = user.role

            return phan_hoi(
                data={'user_id': user.id, 'username': user.username,
                      'role': user.role},
                message='Đăng nhập thành công'
            )

        # ── Đăng xuất ──
        if path.endswith('/logout/'):
            request.session.flush()
            return phan_hoi(message='Đăng xuất thành công')

        return phan_hoi(error='Endpoint không tồn tại', status=404)

    def get(self, request):
        """GET /api/auth/profile/"""
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        try:
            emp = Employee.objects.select_related('department').get(user=user)
            emp_data = {
                'full_name':  emp.full_name,
                'phone':      emp.phone,
                'department': emp.department.name,
                'shift':      emp.shift,
                'salary':     float(emp.salary),
            }
        except Employee.DoesNotExist:
            emp_data = None

        return phan_hoi(data={
            'user_id':  user.id,
            'username': user.username,
            'email':    user.email,
            'role':     user.role,
            'employee': emp_data,
        })

    def put(self, request):
        """PUT /api/auth/profile/ | PUT /api/auth/change-password/"""
        path = request.path
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        # ── Đổi mật khẩu ──
        if path.endswith('/change-password/'):
            mat_khau_cu = data.get('old_password')
            mat_khau_moi = data.get('new_password')
            if not kiem_tra_mat_khau(user, mat_khau_cu):
                return phan_hoi(error='Mật khẩu cũ không đúng', status=400)
            user.password = ma_hoa_mat_khau(mat_khau_moi)
            user.save()
            return phan_hoi(message='Đổi mật khẩu thành công')

        # ── Cập nhật hồ sơ ──
        user.email = data.get('email', user.email)
        user.save()
        try:
            emp = Employee.objects.get(user=user)
            emp.full_name = data.get('full_name', emp.full_name)
            emp.phone     = data.get('phone',     emp.phone)
            emp.save()
        except Employee.DoesNotExist:
            pass
        return phan_hoi(message='Cập nhật hồ sơ thành công')


# ================================================================== #
#  2. USER – Quản lý tài khoản (Quản lý)                             #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):

    def get(self, request, pk=None):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        if pk:
            try:
                u = User.objects.get(id=pk)
                return phan_hoi(data={'id': u.id, 'username': u.username,
                                      'email': u.email, 'role': u.role,
                                      'is_active': u.is_active})
            except User.DoesNotExist:
                return phan_hoi(error='Không tìm thấy tài khoản', status=404)

        ds = User.objects.all()
        return phan_hoi(data=list(ds.values(
            'id', 'username', 'email', 'role', 'is_active', 'created_at')))

    def post(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        ok, msg = kiem_tra_truong_bat_buoc(data,
                  ['username', 'password', 'email', 'role'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        if User.objects.filter(username=data['username']).exists():
            return phan_hoi(error='Username đã tồn tại', status=400)

        u = User.objects.create(
            username=data['username'], password=ma_hoa_mat_khau(data['password']),
            email=data['email'],       role=data['role'])
        return phan_hoi(data={'id': u.id, 'username': u.username},
                        message='Tạo tài khoản thành công', status=201)

    def put(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            u = User.objects.get(id=pk)
        except User.DoesNotExist:
            return phan_hoi(error='Không tìm thấy tài khoản', status=404)

        u.email     = data.get('email',     u.email)
        u.role      = data.get('role',      u.role)
        u.is_active = data.get('is_active', u.is_active)
        if data.get('password'):
            u.password = ma_hoa_mat_khau(data['password'])
        u.save()
        return phan_hoi(message='Cập nhật tài khoản thành công')

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            u = User.objects.get(id=pk)
            u.is_active = False    # Vô hiệu hóa, không xóa hẳn
            u.save()
            return phan_hoi(message='Vô hiệu hóa tài khoản thành công')
        except User.DoesNotExist:
            return phan_hoi(error='Không tìm thấy tài khoản', status=404)


# ================================================================== #
#  3. DEPARTMENT – Quản lý phòng ban                                  #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class DepartmentView(View):

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                d = Department.objects.get(id=pk)
                return phan_hoi(data={'id': d.id, 'name': d.name,
                                      'description': d.description})
            except Department.DoesNotExist:
                return phan_hoi(error='Không tìm thấy phòng ban', status=404)
        return phan_hoi(data=list(Department.objects.all().values()))

    def post(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name'])
        if not ok:
            return phan_hoi(error=msg, status=400)
        d = Department.objects.create(
            name=data['name'], description=data.get('description', ''))
        return phan_hoi(data={'id': d.id, 'name': d.name},
                        message='Thêm phòng ban thành công', status=201)

    def put(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            d = Department.objects.get(id=pk)
            d.name        = data.get('name',        d.name)
            d.description = data.get('description', d.description)
            d.save()
            return phan_hoi(message='Cập nhật phòng ban thành công')
        except Department.DoesNotExist:
            return phan_hoi(error='Không tìm thấy phòng ban', status=404)

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            Department.objects.get(id=pk).delete()
            return phan_hoi(message='Xóa phòng ban thành công')
        except Department.DoesNotExist:
            return phan_hoi(error='Không tìm thấy phòng ban', status=404)


# ================================================================== #
#  4. EMPLOYEE – Quản lý nhân viên                                    #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class EmployeeView(View):

    def _to_dict(self, e):
        return {'id': e.id, 'full_name': e.full_name, 'phone': e.phone,
                'department': e.department.name, 'shift': e.shift,
                'salary': float(e.salary), 'status': e.status,
                'username': e.user.username}

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                e = Employee.objects.select_related('user','department').get(id=pk)
                return phan_hoi(data=self._to_dict(e))
            except Employee.DoesNotExist:
                return phan_hoi(error='Không tìm thấy nhân viên', status=404)
        ds = Employee.objects.select_related('user','department').all()
        return phan_hoi(data=list(map(self._to_dict, ds)))

    def post(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data,
                  ['username','password','email','department_id',
                   'full_name','phone','hire_date'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        u = User.objects.create(
            username=data['username'], password=ma_hoa_mat_khau(data['password']),
            email=data['email'],       role='le_tan')
        emp = Employee.objects.create(
            user=u, department_id=data['department_id'],
            full_name=data['full_name'], phone=data['phone'],
            salary=data.get('salary', 0), hire_date=data['hire_date'],
            shift=data.get('shift', 'sang'))
        return phan_hoi(data={'id': emp.id, 'full_name': emp.full_name},
                        message='Thêm nhân viên thành công', status=201)

    def put(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            emp = Employee.objects.get(id=pk)
            emp.full_name     = data.get('full_name',     emp.full_name)
            emp.phone         = data.get('phone',         emp.phone)
            emp.salary        = data.get('salary',        emp.salary)
            emp.shift         = data.get('shift',         emp.shift)
            emp.status        = data.get('status',        emp.status)
            if data.get('department_id'):
                emp.department_id = data['department_id']
            emp.save()
            return phan_hoi(message='Cập nhật nhân viên thành công')
        except Employee.DoesNotExist:
            return phan_hoi(error='Không tìm thấy nhân viên', status=404)

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            emp = Employee.objects.get(id=pk)
            emp.status = 'nghi_viec'
            emp.save()
            emp.user.is_active = False
            emp.user.save()
            return phan_hoi(message='Đã vô hiệu hóa nhân viên')
        except Employee.DoesNotExist:
            return phan_hoi(error='Không tìm thấy nhân viên', status=404)


# ================================================================== #
#  5. CUSTOMER – Quản lý khách hàng                                   #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class CustomerView(View):

    def _to_dict(self, c):
        return {'id': c.id, 'full_name': c.full_name, 'phone': c.phone,
                'email': c.email, 'id_card': c.id_card,
                'address': c.address, 'customer_type': c.customer_type}

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                return phan_hoi(data=self._to_dict(Customer.objects.get(id=pk)))
            except Customer.DoesNotExist:
                return phan_hoi(error='Không tìm thấy khách hàng', status=404)

        qs = Customer.objects.all()
        # Lọc theo loại khách (VIP / regular)
        customer_type = request.GET.get('customer_type')
        if customer_type:
            qs = qs.filter(customer_type=customer_type)
        # Tìm theo số điện thoại
        phone = request.GET.get('phone')
        if phone:
            qs = qs.filter(phone__icontains=phone)

        return phan_hoi(data=list(map(self._to_dict, qs)))

    def post(self, request):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['full_name','phone','id_card'])
        if not ok:
            return phan_hoi(error=msg, status=400)
        if Customer.objects.filter(id_card=data['id_card']).exists():
            return phan_hoi(error='Số CCCD đã tồn tại', status=400)
        if Customer.objects.filter(phone=data['phone']).exists():
            return phan_hoi(error='Số điện thoại đã tồn tại', status=400)

        c = Customer.objects.create(
            full_name=data['full_name'],   phone=data['phone'],
            email=data.get('email'),       id_card=data['id_card'],
            address=data.get('address',''),
            customer_type=data.get('customer_type','regular'))
        return phan_hoi(data={'id': c.id, 'full_name': c.full_name},
                        message='Thêm khách hàng thành công', status=201)

    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            c = Customer.objects.get(id=pk)
            c.full_name     = data.get('full_name',     c.full_name)
            c.phone         = data.get('phone',         c.phone)
            c.email         = data.get('email',         c.email)
            c.address       = data.get('address',       c.address)
            c.customer_type = data.get('customer_type', c.customer_type)
            c.save()
            return phan_hoi(message='Cập nhật khách hàng thành công')
        except Customer.DoesNotExist:
            return phan_hoi(error='Không tìm thấy khách hàng', status=404)

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            Customer.objects.get(id=pk).delete()
            return phan_hoi(message='Xóa khách hàng thành công')
        except Customer.DoesNotExist:
            return phan_hoi(error='Không tìm thấy khách hàng', status=404)


# ================================================================== #
#  6. ROOM TYPE – Quản lý loại phòng                                  #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class RoomTypeView(View):

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                rt = RoomType.objects.get(id=pk)
                return phan_hoi(data={
                    'id': rt.id, 'name': rt.name,
                    'price_per_night': float(rt.price_per_night),
                    'capacity': rt.capacity, 'description': rt.description})
            except RoomType.DoesNotExist:
                return phan_hoi(error='Không tìm thấy loại phòng', status=404)
        ds = RoomType.objects.all()
        return phan_hoi(data=list(map(lambda rt: {
            'id': rt.id, 'name': rt.name,
            'price_per_night': float(rt.price_per_night),
            'capacity': rt.capacity}, ds)))

    def post(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name','price_per_night'])
        if not ok:
            return phan_hoi(error=msg, status=400)
        rt = RoomType.objects.create(
            name=data['name'], price_per_night=data['price_per_night'],
            capacity=data.get('capacity',2),
            description=data.get('description',''))
        return phan_hoi(data={'id': rt.id, 'name': rt.name},
                        message='Thêm loại phòng thành công', status=201)

    def put(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            rt = RoomType.objects.get(id=pk)
            rt.name            = data.get('name',            rt.name)
            rt.price_per_night = data.get('price_per_night', rt.price_per_night)
            rt.capacity        = data.get('capacity',        rt.capacity)
            rt.description     = data.get('description',     rt.description)
            rt.save()
            return phan_hoi(message='Cập nhật loại phòng thành công')
        except RoomType.DoesNotExist:
            return phan_hoi(error='Không tìm thấy loại phòng', status=404)

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            RoomType.objects.get(id=pk).delete()
            return phan_hoi(message='Xóa loại phòng thành công')
        except RoomType.DoesNotExist:
            return phan_hoi(error='Không tìm thấy loại phòng', status=404)


# ================================================================== #
#  7. ROOM – Quản lý phòng                                            #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class RoomView(View):

    def _to_dict(self, r):
        return {'id': r.id, 'room_number': r.room_number, 'floor': r.floor,
                'status': r.status, 'room_type': r.room_type.name,
                'price_per_night': float(r.room_type.price_per_night),
                'capacity': r.room_type.capacity}

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                r = Room.objects.select_related('room_type').get(id=pk)
                return phan_hoi(data=self._to_dict(r))
            except Room.DoesNotExist:
                return phan_hoi(error='Không tìm thấy phòng', status=404)

        qs = Room.objects.select_related('room_type').all()
        # Lọc theo trạng thái (vd: ?status=trong)
        status = request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return phan_hoi(data=list(map(self._to_dict, qs)))

    def post(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data,
                  ['room_type_id','room_number','floor'])
        if not ok:
            return phan_hoi(error=msg, status=400)
        if Room.objects.filter(room_number=data['room_number']).exists():
            return phan_hoi(error='Số phòng đã tồn tại', status=400)
        r = Room.objects.create(
            room_type_id=data['room_type_id'],
            room_number=data['room_number'],
            floor=data['floor'],
            status=data.get('status','trong'))
        return phan_hoi(data={'id': r.id, 'room_number': r.room_number},
                        message='Thêm phòng thành công', status=201)

    def put(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            r = Room.objects.get(id=pk)
            if data.get('room_type_id'):
                r.room_type_id = data['room_type_id']
            r.floor = data.get('floor', r.floor)
            r.save()
            return phan_hoi(message='Cập nhật phòng thành công')
        except Room.DoesNotExist:
            return phan_hoi(error='Không tìm thấy phòng', status=404)

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            Room.objects.get(id=pk).delete()
            return phan_hoi(message='Xóa phòng thành công')
        except Room.DoesNotExist:
            return phan_hoi(error='Không tìm thấy phòng', status=404)


@method_decorator(csrf_exempt, name='dispatch')
class RoomStatusView(View):
    """PUT /api/rooms/<pk>/status/ – Cập nhật trạng thái phòng"""

    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        trang_thai = data.get('status')
        if not trang_thai:
            return phan_hoi(error='Thiếu trường status', status=400)

        svc = RoomService()
        ok, room = svc.cap_nhat_trang_thai(pk, trang_thai)
        if not ok:
            return phan_hoi(error='Không tìm thấy phòng', status=404)
        return phan_hoi(
            data={'id': room.id, 'room_number': room.room_number,
                  'status': room.status},
            message='Cập nhật trạng thái phòng thành công')


# ================================================================== #
#  8. BOOKING – Quản lý đặt phòng                                     #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class BookingView(View):

    def _to_dict(self, b):
        return {'id': b.id, 'customer': b.customer.full_name,
                'room_number': b.room.room_number,
                'check_in': str(b.check_in), 'check_out': str(b.check_out),
                'status': b.status, 'note': b.note,
                'created_at': str(b.created_at)}

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        if pk:
            try:
                b = Booking.objects.select_related(
                    'customer','room','room__room_type').get(id=pk)
                svc    = BookingWorkflowService()
                so_dem = svc.tinh_so_dem(b.check_in, b.check_out)
                return phan_hoi(data={
                    **self._to_dict(b),
                    'so_dem':     so_dem,
                    'tien_phong': svc.tinh_tien_phong(b),
                    'tien_dv':    svc.tinh_tien_dich_vu(b.id),
                })
            except Booking.DoesNotExist:
                return phan_hoi(error='Không tìm thấy booking', status=404)

        qs = Booking.objects.select_related(
            'customer','room','room__room_type').all()
        status = request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return phan_hoi(data=list(map(self._to_dict, qs)))

    def post(self, request):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        ok, msg = kiem_tra_truong_bat_buoc(data,
                  ['customer_id','room_id','check_in','check_out'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        ok, msg = kiem_tra_ngay(data['check_in'], data['check_out'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        # Gắn nhân viên tạo booking
        try:
            emp = Employee.objects.get(user=user)
            data['created_by_id'] = emp.id
        except Employee.DoesNotExist:
            data['created_by_id'] = None

        svc = BookingWorkflowService()
        booking, err_msg = svc.tao_booking(data)
        if not booking:
            return phan_hoi(error=err_msg, status=400)

        # Tự động tạo hóa đơn
        booking_full = Booking.objects.select_related(
            'room','room__room_type').get(id=booking.id)
        inv_svc = InvoiceService()
        invoice = inv_svc.tao_hoa_don(booking_full)

        return phan_hoi(
            data={'booking_id': booking.id, 'status': booking.status,
                  'tien_phong': float(invoice.room_charge),
                  'tong_tien':  float(invoice.total)},
            message='Đặt phòng thành công', status=201)

    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            b = Booking.objects.get(id=pk)
            b.note = data.get('note', b.note)
            b.save()
            return phan_hoi(message='Cập nhật booking thành công')
        except Booking.DoesNotExist:
            return phan_hoi(error='Không tìm thấy booking', status=404)

    def delete(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        svc = BookingWorkflowService()
        b, err_msg = svc.huy_booking(pk)
        if not b:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(message='Hủy booking thành công')


# ── Confirm / Cancel / Check-in / Check-out ───────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class BookingConfirmView(View):
    """PUT /api/bookings/<pk>/confirm/"""
    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        svc = BookingWorkflowService()
        b, err_msg = svc.xac_nhan_booking(pk)
        if not b:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(data={'id': b.id, 'status': b.status},
                        message='Xác nhận đặt phòng thành công')


@method_decorator(csrf_exempt, name='dispatch')
class BookingCancelView(View):
    """PUT /api/bookings/<pk>/cancel/"""
    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        svc = BookingWorkflowService()
        b, err_msg = svc.huy_booking(pk)
        if not b:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(data={'id': b.id, 'status': b.status},
                        message='Hủy đặt phòng thành công')


@method_decorator(csrf_exempt, name='dispatch')
class BookingCheckinView(View):
    """PUT /api/bookings/<pk>/check-in/"""
    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        svc = BookingWorkflowService()
        b, err_msg = svc.check_in(pk)
        if not b:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(data={'id': b.id, 'status': b.status},
                        message='Check-in thành công')


@method_decorator(csrf_exempt, name='dispatch')
class BookingCheckoutView(View):
    """PUT /api/bookings/<pk>/check-out/"""
    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        svc = BookingWorkflowService()
        b, err_msg = svc.check_out(pk)
        if not b:
            return phan_hoi(error=err_msg, status=400)
        return phan_hoi(data={'id': b.id, 'status': b.status},
                        message='Check-out thành công')


# ================================================================== #
#  9. SERVICE – Quản lý dịch vụ                                       #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class ServiceView(View):

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                s = Service.objects.get(id=pk)
                return phan_hoi(data={'id': s.id, 'name': s.name,
                                      'price': float(s.price),
                                      'description': s.description,
                                      'is_active': s.is_active})
            except Service.DoesNotExist:
                return phan_hoi(error='Không tìm thấy dịch vụ', status=404)
        ds = Service.objects.filter(is_active=True)
        return phan_hoi(data=list(map(lambda s: {
            'id': s.id, 'name': s.name, 'price': float(s.price),
            'description': s.description}, ds)))

    def post(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name','price'])
        if not ok:
            return phan_hoi(error=msg, status=400)
        s = Service.objects.create(
            name=data['name'], price=data['price'],
            description=data.get('description',''))
        return phan_hoi(data={'id': s.id, 'name': s.name},
                        message='Thêm dịch vụ thành công', status=201)

    def put(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            s = Service.objects.get(id=pk)
            s.name        = data.get('name',        s.name)
            s.price       = data.get('price',       s.price)
            s.description = data.get('description', s.description)
            s.is_active   = data.get('is_active',   s.is_active)
            s.save()
            return phan_hoi(message='Cập nhật dịch vụ thành công')
        except Service.DoesNotExist:
            return phan_hoi(error='Không tìm thấy dịch vụ', status=404)

    def delete(self, request, pk):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err
        try:
            s = Service.objects.get(id=pk)
            s.is_active = False    # Xóa mềm
            s.save()
            return phan_hoi(message='Xóa dịch vụ thành công')
        except Service.DoesNotExist:
            return phan_hoi(error='Không tìm thấy dịch vụ', status=404)


# ================================================================== #
#  10. BOOKING SERVICE – Dịch vụ theo booking                         #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class BookingServiceView(View):
    """GET/POST /api/bookings/<pk>/services/"""

    def get(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        ds = BookingServiceModel.objects.filter(
            booking_id=pk).select_related('service')
        return phan_hoi(data=list(map(lambda bs: {
            'id': bs.id, 'service': bs.service.name,
            'quantity': bs.quantity, 'subtotal': float(bs.subtotal),
            'used_at': str(bs.used_at)}, ds)))

    def post(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        ok, msg = kiem_tra_truong_bat_buoc(data, ['service_id','quantity'])
        if not ok:
            return phan_hoi(error=msg, status=400)

        try:
            s = Service.objects.get(id=data['service_id'])
        except Service.DoesNotExist:
            return phan_hoi(error='Không tìm thấy dịch vụ', status=404)

        quantity = int(data['quantity'])
        subtotal = float(s.price) * quantity

        bs = BookingServiceModel.objects.create(
            booking_id=pk, service=s,
            quantity=quantity, subtotal=subtotal)

        # Cập nhật lại hóa đơn
        try:
            b = Booking.objects.select_related(
                'room','room__room_type').get(id=pk)
            InvoiceService().cap_nhat_hoa_don(b)
        except Booking.DoesNotExist:
            pass

        return phan_hoi(
            data={'id': bs.id, 'service': s.name,
                  'quantity': quantity, 'subtotal': subtotal},
            message='Thêm dịch vụ thành công', status=201)


@method_decorator(csrf_exempt, name='dispatch')
class BookingServiceDetailView(View):
    """PUT/DELETE /api/booking-services/<pk>/"""

    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            bs = BookingServiceModel.objects.select_related('service').get(id=pk)
            bs.quantity = data.get('quantity', bs.quantity)
            bs.subtotal = float(bs.service.price) * int(bs.quantity)
            bs.save()
            return phan_hoi(message='Cập nhật dịch vụ thành công')
        except BookingServiceModel.DoesNotExist:
            return phan_hoi(error='Không tìm thấy', status=404)

    def delete(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        try:
            BookingServiceModel.objects.get(id=pk).delete()
            return phan_hoi(message='Xóa dịch vụ thành công')
        except BookingServiceModel.DoesNotExist:
            return phan_hoi(error='Không tìm thấy', status=404)


# ================================================================== #
#  11. INVOICE – Quản lý hóa đơn                                      #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class InvoiceView(View):

    def _to_dict(self, inv):
        return {'id': inv.id, 'booking_id': inv.booking_id,
                'customer': inv.booking.customer.full_name,
                'room_number': inv.booking.room.room_number,
                'room_charge': float(inv.room_charge),
                'service_charge': float(inv.service_charge),
                'total': float(inv.total),
                'payment_status': inv.payment_status,
                'payment_method': inv.payment_method,
                'paid_at': str(inv.paid_at) if inv.paid_at else None}

    def get(self, request, pk=None):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        if pk:
            try:
                inv = Invoice.objects.select_related(
                    'booking__customer','booking__room').get(id=pk)
                return phan_hoi(data=self._to_dict(inv))
            except Invoice.DoesNotExist:
                return phan_hoi(error='Không tìm thấy hóa đơn', status=404)

        ds = Invoice.objects.select_related(
            'booking__customer','booking__room').all()
        return phan_hoi(data=list(map(self._to_dict, ds)))

    def post(self, request):
        """POST /api/invoices/ – Tạo hóa đơn thủ công"""
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err
        try:
            b = Booking.objects.select_related(
                'room','room__room_type').get(id=data.get('booking_id'))
        except Booking.DoesNotExist:
            return phan_hoi(error='Không tìm thấy booking', status=404)
        inv = InvoiceService().tao_hoa_don(b)
        return phan_hoi(data=self._to_dict(Invoice.objects.select_related(
            'booking__customer','booking__room').get(id=inv.id)),
            message='Tạo hóa đơn thành công', status=201)


@method_decorator(csrf_exempt, name='dispatch')
class InvoiceByBookingView(View):
    """GET /api/bookings/<pk>/invoice/"""

    def get(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        try:
            inv = Invoice.objects.select_related(
                'booking__customer','booking__room').get(booking_id=pk)
            return phan_hoi(data={
                'id': inv.id, 'booking_id': inv.booking_id,
                'customer': inv.booking.customer.full_name,
                'room_number': inv.booking.room.room_number,
                'room_charge': float(inv.room_charge),
                'service_charge': float(inv.service_charge),
                'total': float(inv.total),
                'payment_status': inv.payment_status})
        except Invoice.DoesNotExist:
            return phan_hoi(error='Chưa có hóa đơn cho booking này', status=404)


@method_decorator(csrf_exempt, name='dispatch')
class InvoicePayView(View):
    """PUT /api/invoices/<pk>/pay/"""

    def put(self, request, pk):
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        phuong_thuc = data.get('payment_method', 'tien_mat')
        svc = InvoiceService()
        inv, err_msg = svc.thanh_toan(pk, phuong_thuc)
        if not inv:
            return phan_hoi(error=err_msg, status=400)

        return phan_hoi(
            data={'invoice_id': inv.id, 'total': float(inv.total),
                  'payment_method': inv.payment_method,
                  'paid_at': str(inv.paid_at)},
            message='Thanh toán thành công')


# ================================================================== #
#  12. REPORT – Thống kê                                              #
# ================================================================== #
@method_decorator(csrf_exempt, name='dispatch')
class ReportView(View):
    """
    GET /api/reports/revenue/
    GET /api/reports/room-status/
    GET /api/reports/booking-statistics/
    GET /api/reports/top-services/
    """

    def get(self, request):
        user, err = kiem_tra_role(request, ['quan_ly'])
        if err:
            return err

        path = request.path
        svc  = ReportService()

        # Thống kê doanh thu
        if path.endswith('/revenue/'):
            tu_ngay  = request.GET.get('tu_ngay')
            den_ngay = request.GET.get('den_ngay')
            return phan_hoi(data=svc.thong_ke_doanh_thu(tu_ngay, den_ngay))

        # Thống kê tình trạng phòng
        if path.endswith('/room-status/'):
            return phan_hoi(data=svc.thong_ke_trang_thai_phong())

        # Thống kê đặt phòng
        if path.endswith('/booking-statistics/'):
            tu_ngay  = request.GET.get('tu_ngay')
            den_ngay = request.GET.get('den_ngay')
            return phan_hoi(data=svc.thong_ke_dat_phong(tu_ngay, den_ngay))

        # Dịch vụ sử dụng nhiều nhất
        if path.endswith('/top-services/'):
            top_n = int(request.GET.get('top', 5))
            return phan_hoi(data=svc.top_dich_vu(top_n))

        return phan_hoi(error='Endpoint không tồn tại', status=404)

