from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from guide.models import Guide, GuideCategory

class GuideCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )

class GuideAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'download')

    def download(self, obj):
        return format_html(
            '<a class="button" href="{}">下载</a>',
            reverse('guide-detail', args=[obj.pk]),
        )

admin.site.register(Guide, GuideAdmin)
admin.site.register(GuideCategory, GuideCategoryAdmin)
