from django.db import models
from user.models import User

class Activity(models.Model):
    time_start = models.DateTimeField(verbose_name='起始时间')
    time_end = models.DateTimeField(verbose_name='结束时间')
    location = models.CharField(max_length=200, verbose_name='活动地点')
    name = models.CharField(max_length=30, verbose_name='名称', unique=True)
    description = models.TextField(verbose_name='描述')
    form_metas = models.TextField(verbose_name='报名表单')
    open_for_enrollment = models.BooleanField(default=False, verbose_name='开放报名？')
    participants_total_limit = models.IntegerField(null=True, default=None, blank=True, verbose_name='参与者总数限制')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    
    def __str__(self):
        return self.name

    def is_full(self):
        if self.participants_total_limit is None:
            return False
        return Enrollment.objects.filter(activity=self).count() >= self.participants_total_limit

    class Meta:
        ordering = ('-created', '-id')
        verbose_name = '活动'
        verbose_name_plural = '活动'

class Enrollment(models.Model):
    enroll_time = models.DateTimeField(auto_now_add=True, verbose_name='报名时间')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='enrollments', verbose_name='活动')
    participating_metas = models.TextField(verbose_name='参与信息')

    def __str__(self):
        return '{}报名{}'.format(self.user.get_fullname(), self.activity.name)
    
    class Meta:
        unique_together = (('activity', 'user'), )
        ordering = ('-enroll_time', '-id')
        verbose_name = '报名记录'
        verbose_name_plural = '报名记录'

class ClockinMeta(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活动', related_name='clockins')
    generated_key = models.CharField(max_length=255, null=True, blank=True, verbose_name='打卡码')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    label = models.CharField(max_length=32, verbose_name='打卡标签')
    changed = models.DateTimeField(auto_now=True, verbose_name='修改日期')
    from_time = models.DateTimeField(verbose_name='有效时间（从）')
    to_time = models.DateTimeField(verbose_name='有效时间（到）')

    def __str__(self):
        return '{} {}'.format(self.activity.name, self.label)

    class Meta:
        unique_together = (('activity', 'label'), )
        ordering = ('-created', '-id')
        verbose_name = '打卡项'
        verbose_name_plural = '打卡项'

class ClockinRecord(models.Model):
    clockin_meta = models.ForeignKey(ClockinMeta, on_delete=models.CASCADE, verbose_name='打卡项')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='打卡用户', related_name='clockin_records')
    created = models.DateTimeField(auto_now_add=True, verbose_name='打卡时间')

    class Meta:
        unique_together = (('user', 'clockin_meta'), )
        ordering = ('-created', '-id')
        verbose_name = '打卡历史'
        verbose_name_plural = '打卡历史'

class ClockinStaff(models.Model):
    clockin_meta = models.ForeignKey(ClockinMeta, on_delete=models.CASCADE, verbose_name='打卡项', related_name='clockin_staffs')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='打卡员')

    def __str__(self):
        return '{}负责{}的{}打卡'.format(self.staff.username, self.clockin_meta.activity.name, self.clockin_meta.label)

    class Meta:
        unique_together = (('clockin_meta', 'staff'), )
        verbose_name = '打卡员'
        verbose_name_plural = '打卡员'