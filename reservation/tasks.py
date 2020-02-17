from celery import shared_task
from dateutil import parser
from reservation.models import Reservation, Meetingroom
from rest_framework.serializers import ModelSerializer
from user.models import User
from reservation.apps import ReservationConfig

@shared_task(time_limit=ReservationConfig.reserve_task_timeout, queue='single')
def do_reserve(reserve_from, reserve_to, description, meetingroom_id, user_id):
    reserve_from = parser.parse(reserve_from)
    reserve_to = parser.parse(reserve_to)

    meetingroom = Meetingroom.objects.get(id=meetingroom_id)
    user = User.objects.get(id=user_id)

    reservations = meetingroom.reservations.filter(reserve_to__gt=reserve_from, reserve_from__lt=reserve_to).all()
    for reservation in reservations:
        if max(reservation.reserve_from, reserve_from) < min(reservation.reserve_to, reserve_to):
            return {
                'status': 'fail',
                'detail': '会议室在该时间段已经被占用。'
            }
    
    reservation = Reservation.objects.create(
        user=user,
        reserve_from=reserve_from,
        reserve_to=reserve_to,
        description=description,
        meetingroom=meetingroom
    )
    return {
        'status': 'success',
        'detail': reservation.id
    }