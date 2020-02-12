from django.db import models
from user.models import User

class Activity(models.Model):
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    location = models.CharField(max_length=200)
    name = models.CharField(max_length=30)
    description = models.TextField()
    form_metas = models.TextField()
    open_for_enrollment = models.BooleanField(default=False)
    participants_total_limit = models.IntegerField(null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    def is_full(self):
        if self.participants_total_limit is None:
            return False
        return Enrollment.objects.filter(activity=self).count() >= self.participants_total_limit

    class Meta:
        ordering = ('-created', '-id')

class Enrollment(models.Model):
    enroll_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='enrollments')
    participating_metas = models.TextField()
    
    class Meta:
        unique_together = (('activity', 'user'), )
        ordering = ('-enroll_time', '-id')

class ClockinMeta(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    generated_key = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=32)
    changed = models.DateTimeField(auto_now=True)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()
    need_enrollment = models.BooleanField(default=True)

    class Meta:
        unique_together = (('activity', 'label'), )
        ordering = ('-created', '-id')

class ClockinRecord(models.Model):
    clockin_meta = models.ForeignKey(ClockinMeta, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'clockin_meta'), )
        ordering = ('-created', '-id')