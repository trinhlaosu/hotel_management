"""Serializer exports."""
from hotel_app.serializers.auth import *
from hotel_app.serializers.users import *
from hotel_app.serializers.departments import *
from hotel_app.serializers.employees import *
from hotel_app.serializers.customers import *
from hotel_app.serializers.rooms import *
from hotel_app.serializers.bookings import *
from hotel_app.serializers.invoices import *
from hotel_app.serializers.services import *

# Backward-compatible aliases for service-layer code.
UserModelSerializer = UserSerializer
DepartmentModelSerializer = DepartmentSerializer
EmployeeModelSerializer = EmployeeSerializer
CustomerModelSerializer = CustomerSerializer
RoomTypeModelSerializer = RoomTypeSerializer
RoomModelSerializer = RoomSerializer
BookingModelSerializer = BookingSerializer
InvoiceModelSerializer = InvoiceSerializer
ServiceModelSerializer = ServiceSerializer
BookingServiceModelSerializer = BookingServiceSerializer
