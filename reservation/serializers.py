from rest_framework import serializers
from reservation.models import Reservation, Meetingroom
from django.utils import timezone
from datetime import timedelta

class MeetingroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meetingroom
        fields = (
            'id',
            'name',
            'location',
            'seats_count',
            'label',
            'description'
        )

class ReservationSerializer(serializers.ModelSerializer):
    meetingroom = MeetingroomSerializer(read_only=True)
    meetingroom_object = serializers.PrimaryKeyRelatedField(queryset=Meetingroom.objects.all(), write_only=True)

    class Meta:
        model = Reservation
        fields = (
            'id',
            'user',
            'meetingroom',
            'meetingroom_object',
            'reserve_from',
            'reserve_to',
            'description'
        )
        read_only_fields = ('user', )
    
    def validate(self, data):
        reserve_from = data['reserve_from'].replace(second=0, microsecond=0, minute=data['reserve_from'].time().minute // 5 * 5)
        reserve_to = data['reserve_to'].replace(second=0, microsecond=0, minute=data['reserve_to'].time().minute // 5 * 5)
        unit = timedelta(minutes=5)
        if reserve_from <= timezone.now():
            raise serializers.ValidationError('开始时间必须在现在以后。')
        delta = reserve_to - reserve_from
        if delta < 2 * unit or delta > 36 * unit:
            raise serializers.ValidationError('预约会议时间不得少于10分钟，不得超过3小时。')
        
        reservations = data['meetingroom_object'].reservations.filter(reserve_to__gt=reserve_from, reserve_from__lt=reserve_to).all()
        for reservation in reservations:
            if max(reservation.reserve_from, reserve_from) < min(reservation.reserve_to, reserve_to):
                raise serializers.ValidationError('该时间段与该会议室的某些会议时间段存在冲突，请重新选择会议室或时间段。')
        
        validated_data = {
            'reserve_from': reserve_from,
            'reserve_to': reserve_to,
            'meetingroom': data['meetingroom_object'],
            'description': data['description']
        }

        return validated_data
