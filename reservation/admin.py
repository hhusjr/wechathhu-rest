from django.contrib import admin
from reservation.models import Reservation, Meetingroom
from wechathhu.admin.filters import DateTimeFilter
from dateutil import parser

class ReservationTimeRangeFilter(DateTimeFilter):
    title = '冲突查询'
    parameter_name = 'time_range'

    def queryset(self, request, queryset):
        reserve_from = self.used_parameters.get(self.lookup_kwarg_since)
        reserve_to = self.used_parameters.get(self.lookup_kwarg_until)
        
        if reserve_from is None or reserve_to is None:
            return queryset.all()

        reserve_from = parser.parse(reserve_from)
        reserve_to = parser.parse(reserve_to)

        contradict_pks = []
        reservations = queryset.filter(reserve_to__gt=reserve_from, reserve_from__lt=reserve_to).all()
        for reservation in reservations:
            if max(reservation.reserve_from, reserve_from) < min(reservation.reserve_to, reserve_to):
                contradict_pks.append(reservation.pk)

        return queryset.filter(pk__in=contradict_pks)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'meetingroom', 'reserve_from', 'reserve_to', 'meetingroom__seats_count', 'meetingroom__location', 'description', 'created')
    list_filter = ('meetingroom', ReservationTimeRangeFilter)

    def meetingroom__seats_count(self, obj):
        return obj.meetingroom.seats_count

    def meetingroom__location(self, obj):
        return obj.meetingroom.location

ReservationAdmin.meetingroom__seats_count.short_description = '座位数量'
ReservationAdmin.meetingroom__location.short_description = '位置'

admin.site.register(Reservation, ReservationAdmin)

class MeetingroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'seats_count', 'label', 'description')
    list_filter = ('location', 'seats_count', 'label')

admin.site.register(Meetingroom, MeetingroomAdmin)