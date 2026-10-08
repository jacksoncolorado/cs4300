from django.contrib import admin

from .models import Booking, Movie, Seat


admin.site.register(Movie)
admin.site.register(Seat)
admin.site.register(Booking)
