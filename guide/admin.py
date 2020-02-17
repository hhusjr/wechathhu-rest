from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from guide.models import Guide, GuideCategory

class GuideInline(admin.TabularInline):
    model = Guide

class GuideCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = (GuideInline, )

class GuideAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'download')
    list_filter = ('category', )

    def download(self, obj):
        return format_html(
            '<a class="el-button el-button--default is-circle" href="{}"><i class="fas fa-download"></i></a>',
            reverse('guide-detail', args=[obj.pk]),
        )

GuideAdmin.download.short_description = '下载'

admin.site.register(Guide, GuideAdmin)
admin.site.register(GuideCategory, GuideCategoryAdmin)
