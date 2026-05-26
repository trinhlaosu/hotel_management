"""API routes for the hotel app."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hotel_app.views.auth import AuthViewSet
from hotel_app.views.bookings import BookingViewSet
from hotel_app.views.customers import CustomerViewSet
from hotel_app.views.departments import DepartmentViewSet
from hotel_app.views.employees import EmployeeViewSet
from hotel_app.views.invoices import InvoiceViewSet
from hotel_app.views.reports import ReportViewSet
from hotel_app.views.rooms import RoomTypeViewSet, RoomViewSet
from hotel_app.views.services import BookingServiceViewSet, ServiceViewSet
from hotel_app.views.users import UserViewSet


router = DefaultRouter(trailing_slash=True)
router.register('auth', AuthViewSet, basename='auth')
router.register('users', UserViewSet, basename='users')
router.register('departments', DepartmentViewSet, basename='departments')
router.register('employees', EmployeeViewSet, basename='employees')
router.register('customers', CustomerViewSet, basename='customers')
router.register('room-types', RoomTypeViewSet, basename='room-types')
router.register('rooms', RoomViewSet, basename='rooms')
router.register('services', ServiceViewSet, basename='services')
router.register('bookings', BookingViewSet, basename='bookings')
router.register(
    'booking-services',
    BookingServiceViewSet,
    basename='booking-services',
)
router.register('invoices', InvoiceViewSet, basename='invoices')
router.register('reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
