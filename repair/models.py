from django.db import models
from user.models import User

class FaultCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='分类名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '故障分类'
        verbose_name_plural = '故障分类'

class NotificationUser(models.Model):
    name = models.CharField(max_length=255, verbose_name='被提醒人姓名')
    email = models.EmailField(unique=True, verbose_name='被提醒人邮箱')
    category = models.ForeignKey(FaultCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='故障分类')

    class Meta:
        verbose_name = '邮件提醒'
        verbose_name_plural = '邮件提醒'

class RepairRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='报修人')
    location = models.CharField(max_length=255, verbose_name='故障地点')
    category = models.ForeignKey(FaultCategory, on_delete=models.SET_NULL, null=True, verbose_name='故障分类')
    status = models.IntegerField(choices=(
        (0, '未受理'),
        (1, '处理中'),
        (2, '已解决')
    ), default=0, verbose_name='状态')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    description = models.TextField(verbose_name='故障概要')

    class Meta:
        ordering = ('-created', )
        verbose_name = '报修请求'
        verbose_name_plural = '报修请求'