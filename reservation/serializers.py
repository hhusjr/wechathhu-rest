from rest_framework import serializers
from reservation.models import Reservation, Meetingroom
from django.utils import timezone
from datetime import timedelta
from reservation.tasks import do_reserve
from reservation.apps import ReservationConfig
from celery.exceptions import TimeoutError, TimeLimitExceeded

class MeetingroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meetingroom
        fields = (
            'id',
            'name',
            'seats_count',
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
        reserve_from = data['reserve_from'].replace(second=0, microsecond=0, minute=data['reserve_from'].time().minute // 30 * 30)
        reserve_to = data['reserve_to'].replace(second=0, microsecond=0, minute=data['reserve_to'].time().minute // 30 * 30)
        unit = timedelta(minutes=30)
        if reserve_to <= timezone.now():
            raise serializers.ValidationError('结束时间必须在现在以后。')
        delta = reserve_to - reserve_from
        if delta < 1 * unit or delta > 3 * 2 * unit:
            raise serializers.ValidationError('预约会议时间不得少于30分钟，不得超过3小时。')
            
        validated_data = {
            'reserve_from': reserve_from,
            'reserve_to': reserve_to,
            'meetingroom': data['meetingroom_object'],
            'description': data['description']
        }

        return validated_data

    def create(self, validated_data):
        task = do_reserve.delay(
            reserve_from=validated_data['reserve_from'].isoformat(),
            reserve_to=validated_data['reserve_to'].isoformat(),
            description=validated_data['description'],
            meetingroom_id=validated_data['meetingroom'].id,
            user_id=validated_data['user'].id
        )

        try:
            res = task.get(timeout=ReservationConfig.reserve_task_timeout)
            if res['status'] == 'success':
                return Reservation.objects.get(id=res['detail'])
            elif res['status'] == 'fail':
                raise serializers.ValidationError({
                    'non_field_errors': [res['detail']]
                })
        except (TimeoutError, TimeLimitExceeded, TypeError, KeyError, ValueError):
            raise serializers.ValidationError({
                'non_field_errors': ['预约请求失败，请重试。']
            })