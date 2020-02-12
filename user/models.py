from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)

    REQUIRED_FIELDS = ()

    # Fields provided for API auth
    wechat_open_id = models.CharField(max_length=255, unique=True, null=True)

class UserMeta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meta')
    department = models.CharField(max_length=255, blank=True, null=True)
    post = models.CharField(max_length=255, blank=True, null=True)
    qq = models.PositiveIntegerField(blank=True, null=True)
    wechat = models.CharField(max_length=255, blank=True, null=True)
    tel = models.PositiveIntegerField(blank=True, null=True)
    phone = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    friend_user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('user', 'friend_user'), )