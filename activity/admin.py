from django.contrib import admin
from activity.models import Enrollment, ClockinMeta
from django.urls import reverse, path
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse
from activity.apps import ActivityConfig
from datetime import timedelta
import uuid
from django.utils import timezone
import json
import qrcode
from io import BytesIO
from django.utils.html import format_html
import base64

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('activity', 'user', 'enroll_time', 'participating_metas')
admin.site.register(Enrollment, EnrollmentAdmin)

class ClockinMetaAdmin(admin.ModelAdmin):
    list_display = ('activity', 'label', 'created', 'qrcode')
    actions = ('generate_clockin_qrcode', )

    def get_urls(self):
        return [
            path('<int:pk>/qrcode/', self.admin_site.admin_view(self.generate_clockin_qrcode_view), name='qrcode'),
            path('<int:pk>/qrcode/img/', self.admin_site.admin_view(self.generate_clockin_qrcode_image), name='qrcode_img')
        ] + super().get_urls()

    def qrcode(self, obj):
        return format_html(
            '<a class="button" href="{}">打卡</a>',
            reverse('admin:qrcode', args=[obj.pk]),
        )

    def generate_clockin_qrcode_view(self, request, pk):
        try:
            clockin_meta = ClockinMeta.objects.get(pk=pk)
        except ClockinMeta.DoesNotExist:
            raise Http404

        context = dict(
           self.admin_site.each_context(request),
           qrcode_url=reverse('admin:qrcode_img', kwargs={
               'pk': pk
           }),
           activity=clockin_meta.activity,
           label=clockin_meta.label
        )
        return TemplateResponse(request, 'clockin-qrcode.html', context)

    def generate_clockin_qrcode_image(self, request, pk):
        try:
            clockin_meta = ClockinMeta.objects.get(pk=pk)
        except ClockinMeta.DoesNotExist:
            raise Http404

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

        return HttpResponse(stream, content_type="image/png")

admin.site.register(ClockinMeta, ClockinMetaAdmin)
