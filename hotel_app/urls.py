"""Khai bao cac API cua app hotel."""
from django.urls import path
from hotel_app.views.auth import AuthView
from hotel_app.views.users import UserView
from hotel_app.views.departments import DepartmentView
from hotel_app.views.employees import EmployeeView
from hotel_app.views.customers import CustomerView
from hotel_app.views.rooms import RoomTypeView, RoomView, RoomStatusView
from hotel_app.views.services import (
    ServiceView, BookingServiceView, BookingServiceDetailView,
)
from hotel_app.views.bookings import (
    BookingView, BookingConfirmView, BookingCancelView,
    BookingCheckinView, BookingCheckoutView,
)
from hotel_app.views.invoices import (
    InvoiceView, InvoiceByBookingView, InvoicePayView,
)
from hotel_app.views.reports import ReportView

urlpatterns = [

    # Auth
    path('auth/register/',       AuthView.as_view()),       # POST
    path('auth/login/',          AuthView.as_view()),       # POST
    path('auth/logout/',         AuthView.as_view()),       # POST
    path('auth/profile/',        AuthView.as_view()),       # GET | PUT
    path('auth/change-password/',AuthView.as_view()),       # PUT

    # User
    path('users/',               UserView.as_view()),       # GET | POST
    path('users/<int:pk>/',      UserView.as_view()),       # GET | PUT | DELETE

    # Department
    path('departments/',         DepartmentView.as_view()), # GET | POST
    path('departments/<int:pk>/',DepartmentView.as_view()), # GET | PUT | DELETE

    # Employee
    path('employees/',           EmployeeView.as_view()),   # GET | POST
    path('employees/<int:pk>/',  EmployeeView.as_view()),   # GET | PUT | DELETE

    # Customer
    path('customers/',           CustomerView.as_view()),   # GET | POST
    path('customers/<int:pk>/',  CustomerView.as_view()),   # GET | PUT | DELETE

    # Room type
    path('room-types/',          RoomTypeView.as_view()),   # GET | POST
    path('room-types/<int:pk>/', RoomTypeView.as_view()),   # GET | PUT | DELETE

    # Room
    path('rooms/',               RoomView.as_view()),       # GET | POST
    path('rooms/<int:pk>/',      RoomView.as_view()),       # GET | PUT | DELETE
    path('rooms/<int:pk>/status/',RoomStatusView.as_view()),# PUT

    # Service
    path('services/',             ServiceView.as_view()),    # GET | POST
    path('services/<int:pk>/',    ServiceView.as_view()),    # GET | PUT | DELETE

    # Booking
    path('bookings/',            BookingView.as_view()),    # GET | POST
    path('bookings/<int:pk>/',   BookingView.as_view()),    # GET | PUT | DELETE
    path('bookings/<int:pk>/confirm/',  BookingConfirmView.as_view()),  # PUT
    path('bookings/<int:pk>/cancel/',   BookingCancelView.as_view()),   # PUT
    path('bookings/<int:pk>/check-in/', BookingCheckinView.as_view()),  # PUT
    path('bookings/<int:pk>/check-out/',BookingCheckoutView.as_view()), # PUT
    path('bookings/<int:pk>/services/', BookingServiceView.as_view()),  # GET | POST
    path('bookings/<int:pk>/invoice/',  InvoiceByBookingView.as_view()),# GET

    # Booking service
    path('booking-services/<int:pk>/', BookingServiceDetailView.as_view()), # PUT | DELETE

    # Invoice
    path('invoices/',            InvoiceView.as_view()),    # GET | POST
    path('invoices/<int:pk>/',   InvoiceView.as_view()),    # GET
    path('invoices/<int:pk>/pay/',InvoicePayView.as_view()),# PUT

    # Report
    path('reports/revenue/',             ReportView.as_view()),  # GET
    path('reports/room-status/',         ReportView.as_view()),  # GET
    path('reports/booking-statistics/',  ReportView.as_view()),  # GET
    path('reports/top-services/',        ReportView.as_view()),  # GET
]

