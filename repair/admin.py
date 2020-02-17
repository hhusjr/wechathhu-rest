from django.contrib import admin
from repair.models import FaultCategory, NotificationUser, RepairRequest

class NotificationUserInline(admin.TabularInline):
    model = NotificationUser

class NotificationUserAdmin(admin.ModelAdmin):
    list_filter = ('category', )
    list_display = ('name', 'email', 'category')

class FaultCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = (NotificationUserInline, )

class RepairRequestAdmin(admin.ModelAdmin):
    list_filter = ('category', 'status')
    list_editable = ('status', )
    list_display = ('user', 'location', 'category', 'status', 'created', 'description')

admin.site.register(FaultCategory, FaultCategoryAdmin)
admin.site.register(NotificationUser, NotificationUserAdmin)
admin.site.register(RepairRequest, RepairRequestAdmin)
