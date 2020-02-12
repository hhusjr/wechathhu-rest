from django.contrib import admin
from reservation.models import Reservation
from user.models import User, Contact, UserMeta

# Register your models here.
admin.site.register(User)
admin.site.register(Contact)
admin.site.register(UserMeta)
