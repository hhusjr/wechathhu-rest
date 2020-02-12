from django.db import models
from user.models import User

class FaultCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

class NotificationUser(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    category = models.ForeignKey(FaultCategory, on_delete=models.SET_NULL, null=True)

class RepairRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=255)
    category = models.ForeignKey(FaultCategory, on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=(
        (0, '未受理'),
        (1, '处理中'),
        (2, '已解决')
    ), default=0)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    class Meta:
        ordering = ('-created', )