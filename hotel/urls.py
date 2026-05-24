"""Khai bao cac API cua app hotel."""
from django.urls import path
from . import views

urlpatterns = [

    # Auth
    path('auth/register/',       views.AuthView.as_view()),       # POST
    path('auth/login/',          views.AuthView.as_view()),       # POST
    path('auth/logout/',         views.AuthView.as_view()),       # POST
    path('auth/profile/',        views.AuthView.as_view()),       # GET | PUT
    path('auth/change-password/',views.AuthView.as_view()),       # PUT

    # User
    path('users/',               views.UserView.as_view()),       # GET | POST
    path('users/<int:pk>/',      views.UserView.as_view()),       # GET | PUT | DELETE

    # Department
    path('departments/',         views.DepartmentView.as_view()), # GET | POST
    path('departments/<int:pk>/',views.DepartmentView.as_view()), # GET | PUT | DELETE

    # Employee
    path('employees/',           views.EmployeeView.as_view()),   # GET | POST
    path('employees/<int:pk>/',  views.EmployeeView.as_view()),   # GET | PUT | DELETE

    # Customer
    path('customers/',           views.CustomerView.as_view()),   # GET | POST
    path('customers/<int:pk>/',  views.CustomerView.as_view()),   # GET | PUT | DELETE

    # Room type
    path('room-types/',          views.RoomTypeView.as_view()),   # GET | POST
    path('room-types/<int:pk>/', views.RoomTypeView.as_view()),   # GET | PUT | DELETE

    # Room
    path('rooms/',               views.RoomView.as_view()),       # GET | POST
    path('rooms/<int:pk>/',      views.RoomView.as_view()),       # GET | PUT | DELETE
    path('rooms/<int:pk>/status/',views.RoomStatusView.as_view()),# PUT

    # Service
    path('services/',             views.ServiceView.as_view()),    # GET | POST
    path('services/<int:pk>/',    views.ServiceView.as_view()),    # GET | PUT | DELETE

    # Booking
    path('bookings/',            views.BookingView.as_view()),    # GET | POST
    path('bookings/<int:pk>/',   views.BookingView.as_view()),    # GET | PUT | DELETE
    path('bookings/<int:pk>/confirm/',  views.BookingConfirmView.as_view()),  # PUT
    path('bookings/<int:pk>/cancel/',   views.BookingCancelView.as_view()),   # PUT
    path('bookings/<int:pk>/check-in/', views.BookingCheckinView.as_view()),  # PUT
    path('bookings/<int:pk>/check-out/',views.BookingCheckoutView.as_view()), # PUT
    path('bookings/<int:pk>/services/', views.BookingServiceView.as_view()),  # GET | POST
    path('bookings/<int:pk>/invoice/',  views.InvoiceByBookingView.as_view()),# GET

    # Booking service
    path('booking-services/<int:pk>/', views.BookingServiceDetailView.as_view()), # PUT | DELETE

    # Invoice
    path('invoices/',            views.InvoiceView.as_view()),    # GET | POST
    path('invoices/<int:pk>/',   views.InvoiceView.as_view()),    # GET
    path('invoices/<int:pk>/pay/',views.InvoicePayView.as_view()),# PUT

    # Report
    path('reports/revenue/',             views.ReportView.as_view()),  # GET
    path('reports/room-status/',         views.ReportView.as_view()),  # GET
    path('reports/booking-statistics/',  views.ReportView.as_view()),  # GET
    path('reports/top-services/',        views.ReportView.as_view()),  # GET
]
