from django.contrib import admin
from repair.models import FaultCategory, NotificationUser, RepairRequest

class FaultCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )

class NotificationUserAdmin(admin.ModelAdmin):
    list_filter = ('category', )
    list_display = ('name', 'email', 'category')

class RepairRequestAdmin(admin.ModelAdmin):
    list_filter = ('category', 'status')
    list_editable = ('status', )
    list_display = ('user', 'location', 'category', 'status', 'created', 'description')

admin.site.register(FaultCategory, FaultCategoryAdmin)
admin.site.register(NotificationUser, NotificationUserAdmin)
admin.site.register(RepairRequest, RepairRequestAdmin)
