from django.db import models
from django.db.models import Q
from user.models import User
from django.utils import timezone

class Meetingroom(models.Model):
    name = models.CharField(max_length=32)
    location = models.CharField(max_length=128)
    seats_count = models.IntegerField()
    label = models.CharField(max_length=32)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meetingroom = models.ForeignKey(Meetingroom, on_delete=models.CASCADE, related_name='reservations')
    reserve_from = models.DateTimeField()
    reserve_to = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    class Meta:
        ordering = ('-created', '-id')