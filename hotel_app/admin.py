from django.contrib import admin
from .models import (User, Department, Employee, Customer,
                     RoomType, Room, Booking, Invoice,
                     Service, BookingService)

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Customer)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Invoice)
admin.site.register(Service)
admin.site.register(BookingService)

