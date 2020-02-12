from django.contrib import admin
from reservation.models import Reservation

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'meetingroom', 'reserve_from', 'reserve_to')

admin.site.register(Reservation, ReservationAdmin)
