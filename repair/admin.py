from django.contrib import admin
from repair.models import FaultCategory, NotificationUser, RepairRequest

admin.site.register(FaultCategory)
admin.site.register(NotificationUser)
admin.site.register(RepairRequest)
