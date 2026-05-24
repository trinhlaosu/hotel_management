"""Customer business logic."""
from hotel_app.models import Customer


class CustomerService:
    def to_dict(self, customer):
        # Chuyen Customer model thanh dict tra ve API.
        return {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'id_card': customer.id_card,
            'address': customer.address,
            'customer_type': customer.customer_type,
        }

    def lay_danh_sach(self, customer_type=None, phone=None):
        # Lay danh sach khach hang, ho tro loc theo loai va so dien thoai.
        qs = Customer.objects.all()
        if customer_type:
            qs = qs.filter(customer_type=customer_type)
        if phone:
            qs = qs.filter(phone__icontains=phone)
        return [self.to_dict(customer) for customer in qs]

    def lay_chi_tiet(self, customer_id):
        # Lay chi tiet khach hang theo id.
        try:
            return self.to_dict(Customer.objects.get(id=customer_id)), None
        except Customer.DoesNotExist:
            return None, 'Không tìm thấy khách hàng'

    def tao_khach_hang(self, data):
        # Tao khach hang moi, chan trung CCCD va so dien thoai.
        if Customer.objects.filter(id_card=data['id_card']).exists():
            return None, 'Số CCCD đã tồn tại'
        if Customer.objects.filter(phone=data['phone']).exists():
            return None, 'Số điện thoại đã tồn tại'

        customer = Customer.objects.create(
            full_name=data['full_name'],
            phone=data['phone'],
            email=data.get('email'),
            id_card=data['id_card'],
            address=data.get('address', ''),
            customer_type=data.get('customer_type', 'regular'),
        )
        return customer, None

    def cap_nhat(self, customer_id, data):
        # Cap nhat thong tin khach hang.
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return None, 'Không tìm thấy khách hàng'

        customer.full_name = data.get('full_name', customer.full_name)
        customer.phone = data.get('phone', customer.phone)
        customer.email = data.get('email', customer.email)
        customer.address = data.get('address', customer.address)
        customer.customer_type = data.get(
            'customer_type', customer.customer_type)
        customer.save()
        return customer, None

    def xoa(self, customer_id):
        # Xoa khach hang khoi CSDL.
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return None, 'Không tìm thấy khách hàng'
        customer.delete()
        return customer, None

