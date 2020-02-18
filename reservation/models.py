from django.db import models
from django.db.models import Q
from user.models import User
from django.utils import timezone

class Meetingroom(models.Model):
    name = models.CharField(max_length=32, verbose_name='会议室名称')
    location = models.CharField(max_length=128, verbose_name='会议室位置')
    seats_count = models.IntegerField(verbose_name='会议室座位数')
    label = models.CharField(max_length=32, verbose_name='会议室标签', blank=True)
    description = models.TextField(verbose_name='会议室简介', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '会议室'
        verbose_name_plural = '会议室'
        ordering = ('name', '-id')
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='预约者')
    meetingroom = models.ForeignKey(Meetingroom, on_delete=models.CASCADE, related_name='reservations', verbose_name='会议室')
    reserve_from = models.DateTimeField(verbose_name='开始时间')
    reserve_to = models.DateTimeField(verbose_name='结束时间')
    created = models.DateTimeField(auto_now_add=True, verbose_name='预约时间')
    description = models.TextField(verbose_name='预约原因')

    class Meta:
        ordering = ('-created', '-id')
        verbose_name = '预约记录'
        verbose_name_plural = '预约记录'