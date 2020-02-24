from django.contrib import admin, messages
from reservation.models import Reservation, Meetingroom
from wechathhu.admin.filters import DateTimeFilter
from dateutil import parser
from datetime import timedelta
from django.utils import timezone
from django import forms
from celery.exceptions import TimeLimitExceeded, TimeoutError
from reservation.tasks import do_reserve
from reservation.apps import ReservationConfig
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse, path
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        if 'initial' not in kwargs:
            kwargs['initial'] = {}
        
        request = self.request
        
        meetingroom_id = request.GET.get('show_meetingroom')
        if meetingroom_id is not None:
            try:
                meetingroom = Meetingroom.objects.get(id=meetingroom_id)
                kwargs['initial']['meetingroom'] = meetingroom
            except (ValueError, Meetingroom.DoesNotExist):
                pass

        reserve_from = request.GET.get('show_reserve_from')
        if reserve_from is not None:
            try:
                kwargs['initial']['reserve_from'] = parser.parse(reserve_from)
            except ValueError:
                pass
        
        reserve_to = request.GET.get('show_reserve_to')
        if reserve_to is not None:
            try:
                kwargs['initial']['reserve_to'] = parser.parse(reserve_to)
            except ValueError:
                pass

        super().__init__(*args, **kwargs)
    
    def clean(self):
        data = super().clean()

        if data.get('reserve_from') is None or data.get('reserve_to') is None or data.get('meetingroom') is None:
            return data

        reserve_from = data['reserve_from'].replace(second=0, microsecond=0, minute=data['reserve_from'].time().minute // 30 * 30)
        reserve_to = data['reserve_to'].replace(second=0, microsecond=0, minute=data['reserve_to'].time().minute // 30 * 30)
        unit = timedelta(minutes=30)
        delta = reserve_to - reserve_from
        if delta < 1 * unit or delta > 3 * 2 * unit:
            raise forms.ValidationError('预约会议时间不得少于30分钟，不得超过3小时。')

        data['reserve_from'] = reserve_from
        data['reserve_to'] = reserve_to

        reservations = data['meetingroom'].reservations.filter(reserve_to__gt=reserve_from, reserve_from__lt=reserve_to).all()
        for reservation in reservations:
            if max(reservation.reserve_from, reserve_from) < min(reservation.reserve_to, reserve_to):
                raise forms.ValidationError('会议室在该时间段已经被占用。')

        return data

class ReservationAdmin(admin.ModelAdmin):
    form = ReservationForm
    autocomplete_fields = ('user', 'meetingroom')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, {
            'meetingrooms': Meetingroom.objects.all()
        })

    def get_urls(self):
        return [
            path('all/', self.admin_site.admin_view(self.get_reservations), name='reservations'),
        ] + super().get_urls()

    def get_reservations(self, request):
        if not super().has_view_permission(request):
            raise PermissionDenied

        try:
            start = parser.parse(request.GET['start'])
            end = parser.parse(request.GET['end'])
        except KeyError:
            return HttpResponseBadRequest('必须给出用于确定查询范围的起止时间。')

        kwargs = {
            'reserve_from__gte': start,
            'reserve_to__lte': end
        }
        pk = request.GET.get('meetingroom', None)
        meetingroom = None
        if pk:
            try:
                meetingroom = Meetingroom.objects.get(pk=pk)
            except Meetingroom.DoesNotExist:
                pass
        if meetingroom:
            kwargs['meetingroom'] = meetingroom
        
        reservations = Reservation.objects.filter(**kwargs).all()

        reservations_display = []
        for reservation in reservations:
            title = reservation.user.get_fullname() + '预约' + reservation.meetingroom.name
            reservations_display.append({
                'start': reservation.reserve_from.isoformat(),
                'end': reservation.reserve_to.isoformat(),
                'title': title,
                'url': reverse('admin:reservation_reservation_change', args=(reservation.id, )),
            })

        return JsonResponse(reservations_display, safe=False)

    def response_add(self, request, obj, post_url_continue=None):
        if messages.get_messages(request):
            return HttpResponseRedirect('.')
        return super().response_add(request, obj, post_url_continue=post_url_continue)

    def save_model(self, request, obj, form, change):
        task = do_reserve.delay(
            reserve_from=obj.reserve_from.isoformat(),
            reserve_to=obj.reserve_to.isoformat(),
            description=obj.description,
            meetingroom_id=obj.meetingroom.id,
            user_id=obj.user.id
        )

        clear_messages = lambda: list(messages.get_messages(request))

        try:
            res = task.get(timeout=ReservationConfig.reserve_task_timeout)
            if res['status'] == 'success':
                return Reservation.objects.get(id=res['detail'])
            elif res['status'] == 'fail':
                clear_messages()
                messages.error(request, res['detail'])
        except (TimeoutError, TimeLimitExceeded, TypeError, KeyError, ValueError):
            clear_messages()
            messages.error(request, res['detail'])

    def has_change_permission(self, request, obj=None):
        return False

    def meetingroom__seats_count(self, obj):
        return obj.meetingroom.seats_count

ReservationAdmin.meetingroom__seats_count.short_description = '座位数量'

admin.site.register(Reservation, ReservationAdmin)

class MeetingroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'seats_count')
    list_filter = ('seats_count', )
    search_fields = ('name', )

admin.site.register(Meetingroom, MeetingroomAdmin)