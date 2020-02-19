from django.contrib import admin
from activity.models import Enrollment, ClockinMeta, ClockinRecord, Activity, ClockinStaff
from django.contrib.admin import helpers, widgets
from django.core.exceptions import PermissionDenied
from django import forms
from django.urls import reverse, path
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse, JsonResponse
from activity.apps import ActivityConfig
from datetime import timedelta
import uuid
from django.utils import timezone
import json
import qrcode
from io import BytesIO
from django.utils.html import format_html, mark_safe
import base64
import math
from activity.utils import match_clockin_query_expr
import json
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from copy import deepcopy

class ActivityFormMetasWidget(forms.Widget):
    class Media:
        js = ('widgets/form_metas.js', )

    template_name = 'admin/widgets/form_metas.html'

class ActivityFormMetasForm(forms.ModelForm):
    class Meta:
        widgets = {
            'form_metas': ActivityFormMetasWidget
        }
        model = Activity
        fields = '__all__'

class ClockinMetaInlineAdmin(admin.StackedInline):
    model = ClockinMeta
    exclude = ('generated_key', )

class ActivityAdmin(admin.ModelAdmin):
    form = ActivityFormMetasForm
    list_display = ('name', 'created', 'open_for_enrollment', 'participants_total_limit', 'location', 'time_start', 'time_end')
    search_fields = ('name', 'location')
    list_filter = ('time_start', )
    list_editable = ('open_for_enrollment', )
    inlines = (ClockinMetaInlineAdmin, )

admin.site.register(Activity, ActivityAdmin)

class EnrollmentResource(resources.ModelResource):
    activity = Field('activity', column_name='活动')
    user = Field('user', column_name='用户')
    enroll_time = Field('enroll_time', column_name='报名时间')

    def __init__(self, activity_obj=None):
        self.activity_obj = activity_obj

        self.fields = deepcopy(self.fields)

        if activity_obj is not None:
            try:
                form_metas = json.loads(activity_obj.form_metas)
                if not isinstance(form_metas, dict):
                    form_metas = {}
            except json.JSONDecodeError:
                form_metas = {}

            self.fields.update({('_participating_meta__' + name): Field(column_name=name) for name in form_metas.keys()})

        super().__init__()

    def resolve_participating_meta(self, field, str_participating_metas):
        try:
            participating_metas = json.loads(str_participating_metas)
            if not isinstance(participating_metas, dict):
                participating_metas = {}
        except json.JSONDecodeError:
            participating_metas = {}
        
        try:
            value = participating_metas[field]
            render = lambda x: ', '.join(x) if isinstance(x, list) else x
            return render(value)
        except (KeyError, IndexError):
            pass

        return None

    def export_field(self, field, obj):
        field_name = self.get_field_name(field)
        if field_name.startswith('_participating_meta__'):
            return self.resolve_participating_meta(field_name.split('__')[1], obj.participating_metas)

        return super().export_field(field, obj)

    class Meta:
        model = Enrollment
        fields = (
            'activity',
            'user',
            'enroll_time'
        )
        widgets = {
            'enroll_time': {'format': r'%Y-%m-%d %H:%M:%S'},
        }

class EnrollmentParticipatingMetasWidget(forms.Widget):
    class Media:
        js = ('widgets/participating_metas.js', )

    template_name = 'admin/widgets/participating_metas.html'
    enrollment = None

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        enrollment = self.enrollment
        activity = enrollment.activity

        try:
            form_metas = json.loads(activity.form_metas)
            if not isinstance(form_metas, dict):
                form_metas = {}
        except json.JSONDecodeError:
            form_metas = {}
        
        try:
            participating_metas = json.loads(enrollment.participating_metas)
            if not isinstance(participating_metas, dict):
                participating_metas = {}
        except json.JSONDecodeError:
            participating_metas = {}

        context_metas = {}
        for name, attributes in form_metas.items():
            if name in participating_metas:
                attributes['value'] = participating_metas[name]
            else:
                attributes['value'] = '' if 'default' not in attributes else attributes['default']

        context.update({
            'form_metas': form_metas.items()
        })
        return context

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        widgets = {
            'participating_metas': EnrollmentParticipatingMetasWidget
        }
        fields = '__all__'

    def __init__(self, data = None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        
        if 'participating_metas' not in self.fields:
            return

        try:
            enrollment = self.instance
        except Enrollment.DoesNotExist:
            enrollment = None
        self.fields['participating_metas'].widget.enrollment = enrollment

class EnrollmentAdmin(ExportMixin, admin.ModelAdmin):
    form = EnrollmentForm
    list_display = ('activity', 'user', 'clockin', 'enroll_time', 'parsed_participating_metas')
    list_filter = ('activity', 'user')
    autocomplete_fields = ('user', 'activity')
    search_fields = ('clockin_filter', )
    search_placeholder = '打卡筛选(且/或/未/括号)'
    resource_class = EnrollmentResource
    list_per_page = 30

    def get_resource_kwargs(self, request, *args, **kwargs):
        try:
            activity = Activity.objects.get(id=request.GET.get('activity__id__exact'))
        except Activity.DoesNotExist:
            activity = None

        return {
            'activity_obj': activity
        }

    def get_exclude(self, request, obj=None):
        exclude = list(self.exclude or [])
        if obj is None:
            exclude.append('participating_metas')
        return exclude

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields or [])
        if obj is not None:
            readonly_fields.append('activity')
        return readonly_fields

    def clockin(self, obj):
        clockins = [x.label for x in obj.activity.clockins.order_by('from_time', 'created').all()]
        user_clockins = [x.clockin_meta.label for x in obj.user.clockin_records.filter(clockin_meta__activity=obj.activity).all()]
        return format_html(' '.join(format_html('<span style="color: {};">{}</span>', 'green' if x in user_clockins else 'red', mark_safe(x)) for x in clockins))

    def get_search_results(self, request, queryset, search_term):
        try:
            activity = Activity.objects.get(id=request.GET.get('activity__id__exact'))
        except Activity.DoesNotExist:
            return queryset, False
        
        clockin_metas = activity.clockins.order_by('from_time', 'created').all()
        enrollments = queryset.all()

        ids = []
        for enrollment in enrollments:
            user_clockins = [x.clockin_meta.label for x in ClockinRecord.objects.filter(user=enrollment.user, clockin_meta__in=clockin_metas)]
            if match_clockin_query_expr(search_term, user_clockins):
                ids.append(enrollment.id)
        
        return queryset.filter(id__in=ids), False

    def parsed_participating_metas(self, obj):
        try:
            participating_metas = json.loads(obj.participating_metas)
            htmls = []
            for key, info in participating_metas.items():
                info_display = ', '.join(info) if isinstance(info, list) else info
                htmls.append(format_html('<p><strong>{}</strong> {}</p>', key, info_display))
        except (json.JSONDecodeError, TypeError, ValueError, IndexError, KeyError):
            return None

        return format_html('<div style="max-height: 80px; overflow-y: scroll;">' + ''.join(htmls) + '</div>')

EnrollmentAdmin.clockin.short_description = '打卡情况'
EnrollmentAdmin.parsed_participating_metas.short_description = '报名信息'

admin.site.register(Enrollment, EnrollmentAdmin)

class ClockinMetaForm(forms.ModelForm):
    class Meta:
        model = ClockinMeta
        fields = '__all__'
        exclude = ('generated_key', )    

    def clean_label(self):
        label = self.cleaned_data['label'].strip()
        stop_words = (
            '#', '(', ')', u'（', u'）',
            u'未', u'且', u'或',
            u'了', u'但'
        )
        is_empty = lambda x: not x.strip()
        for ch in label:
            if ch in stop_words or is_empty(ch):
                raise forms.ValidationError('标签中不得包含空字符或者下列字符之一：' + ' '.join(stop_words))
        return label

class ClockinStaffInline(admin.TabularInline):
    model = ClockinStaff
    autocomplete_fields = ('staff', )

class ClockinMetaAdmin(admin.ModelAdmin):
    list_display = ('activity', 'label', 'created', 'from_time', 'to_time', 'qrcode')
    list_filter = ('activity', )
    exclude = ('generated_key', )    
    actions = ('generate_clockin_qrcode', )
    autocomplete_fields = ('activity', )
    inlines = (ClockinStaffInline, )
    form = ClockinMetaForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.has_perm('activity.view_clockin_meta'):
            return queryset
        return queryset.filter(clockin_staffs__staff=request.user)

    def has_module_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) or obj is None

    def check_and_get_clockin_meta(self, request, pk):
        try:
            clockin_meta = ClockinMeta.objects.get(pk=pk)
        except ClockinMeta.DoesNotExist:
            raise Http404

        if super().has_view_permission(request, clockin_meta) \
            or ClockinStaff.objects.filter(clockin_meta=clockin_meta, staff=request.user).count():
            return clockin_meta
        
        raise PermissionDenied
        
    def get_urls(self):
        return [
            path('<int:pk>/qrcode/', self.admin_site.admin_view(self.generate_clockin_qrcode_view), name='qrcode'),
            path('<int:pk>/qrcode/img/', self.admin_site.admin_view(self.generate_clockin_qrcode_image), name='qrcode_img'),
            path('<int:pk>/qrcode/expiration-timedelta/', self.admin_site.admin_view(self.get_qrcode_expiration_timedelta), name='qrcode_timedelta'),
        ] + super().get_urls()

    def qrcode(self, obj):
        return format_html(
            '<a class="el-button el-button--default is-circle" href="{}" target="_blank"><i class="fas fa-eye"></i></a>',
            reverse('admin:qrcode', args=[obj.pk]),
        )

    def generate_clockin_qrcode_view(self, request, pk):
        clockin_meta = self.check_and_get_clockin_meta(request, pk)

        context = dict(
           self.admin_site.each_context(request),
           qrcode_url=reverse('admin:qrcode_img', kwargs={
               'pk': pk
           }),
           qrcode_timedelta_url=reverse('admin:qrcode_timedelta', kwargs={
               'pk': pk
           }),
           activity=clockin_meta.activity,
           label=clockin_meta.label,
           opts=self.model._meta
        )
        return TemplateResponse(request, 'admin/clockin-qrcode.html', context)

    def get_qrcode_expiration_timedelta(self, request, pk):
        clockin_meta = self.check_and_get_clockin_meta(request, pk)

        return JsonResponse({
            'timedelta': math.ceil((clockin_meta.changed + timedelta(seconds=ActivityConfig.clockin_qrcode_expire) - timezone.now()).total_seconds())
        })

    def generate_clockin_qrcode_image(self, request, pk):
        clockin_meta = self.check_and_get_clockin_meta(request, pk)

        if timezone.now() > clockin_meta.changed + timedelta(seconds=ActivityConfig.clockin_qrcode_expire):
            clockin_meta.generated_key = uuid.uuid4()
            clockin_meta.save()

        data = {
            'activity_id': clockin_meta.activity.id,
            'label': clockin_meta.label,
            'generated_key': str(clockin_meta.generated_key)
        }

        encrypted = base64.b64encode(bytes(json.dumps(data).encode('utf-8')))

        buf = BytesIO()
        img = qrcode.make(encrypted)
        img.save(buf)
        stream = buf.getvalue()

        return HttpResponse(stream, content_type='image/png')

ClockinMetaAdmin.qrcode.short_description = '打卡二维码'

admin.site.register(ClockinMeta, ClockinMetaAdmin)

class ClockinRecordAdmin(admin.ModelAdmin):
    list_display = ('clockin_meta', 'user', 'created')
    raw_id_fields = ('clockin_meta', )
    autocomplete_fields = ('user', )
    list_filter = ('clockin_meta__activity', 'user')

admin.site.register(ClockinRecord, ClockinRecordAdmin)