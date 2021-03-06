from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Concat
from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().annotate(fullname=Concat('last_name', 'first_name'))

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='系所')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '系所'
        verbose_name_plural = '系所'
        ordering = ('name', 'id')

class User(AbstractUser):
    email = models.EmailField(_('email address'), null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='department_users', verbose_name='系所')
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    
    def get_fullname(self):
        if self.last_name is None or self.first_name is None:
            return None
        return '{}{}'.format(self.last_name, self.first_name)

    # Fields provided for API auth
    wechat_open_id = models.CharField(verbose_name='微信openid', max_length=150, unique=True, null=True, blank=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ()

    def __str__(self):
        return '{}-{}'.format(self.username, self.get_fullname())

    class Meta:
        verbose_name = '教师用户'
        verbose_name_plural = '教师用户'
        ordering = ('username', 'id')

class UserMeta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meta', verbose_name='用户')
    post = models.CharField(max_length=255, blank=True, null=True, verbose_name='职位')
    qq = models.CharField(max_length=32, blank=True, null=True, verbose_name='QQ')
    wechat = models.CharField(max_length=255, blank=True, null=True, verbose_name='微信')
    tel = models.CharField(max_length=32, blank=True, null=True, verbose_name='电话')
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='手机')
    description = models.TextField(blank=True, null=True, verbose_name='简介')

    def __str__(self):
        return '{}的通讯录信息'.format(self.user)

    class Meta:
        verbose_name = '教师通讯录信息'
        verbose_name_plural = '教师通讯录信息'

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', verbose_name='用户')
    friend_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='好友')

    def __str__(self):
        return '{}-{}'.format(self.user.username, self.friend_user.username)
    
    class Meta:
        unique_together = (('user', 'friend_user'), )
        verbose_name = '好友关系'
        verbose_name_plural = '好友关系'