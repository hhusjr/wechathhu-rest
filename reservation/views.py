from reservation.models import Meetingroom, Reservation
from rest_framework import views, status, permissions, mixins, generics, viewsets
from rest_framework.viewsets import GenericViewSet
from datetime import timedelta, datetime
from dateutil import parser
from django.utils import timezone
from rest_framework.response import Response
from reservation.serializers import ReservationSerializer
import pytz
from functools import cmp_to_key
from rest_framework.decorators import api_view, permission_classes

@api_view(('GET', ))
@permission_classes((permissions.IsAuthenticated, ))
def available_meetingrooms(request):
    unit = timedelta(minutes=5)
    try:
        target_from_time = parser.parse(request.query_params['time_from'])
        target_from_time = target_from_time.replace(second=0, microsecond=0, minute=target_from_time.time().minute // 5 * 5)
        target_to_time = parser.parse(request.query_params['time_to'])
        target_to_time = target_to_time.replace(second=0, microsecond=0, minute=target_to_time.time().minute // 5 * 5)

        if target_from_time <= timezone.now():
            return Response({
                'detail': '最早的开始时间必须在现在以后。'
            }, status=status.HTTP_400_BAD_REQUEST)
        if target_to_time - target_from_time < 2 * unit:
            return Response({
                'detail': '预约会议时间不得少于10分钟。'
            }, status=status.HTTP_400_BAD_REQUEST)

        kwargs = {}
        if 'people_count' in request.query_params:
            kwargs['seats_count__gte'] = int(request.query_params['people_count'])
        if 'label' in request.query_params:
            kwargs['label__icontains'] = request.query_params['label']
        if 'location' in request.query_params:
            kwargs['location__icontains'] = request.query_params['location']

        if 'length' in request.query_params:
            length_minutes = int(request.query_params['length'])
        else:
            length_minutes = int((target_to_time - target_from_time).total_seconds()) // 60
        length_minutes = length_minutes // 5 * 5

        if length_minutes < 2 * 5 or length_minutes > 36 * 5:
            return Response({
                'detail': '预约会议时间不得少于10分钟，不得超过3小时。'
            }, status=status.HTTP_400_BAD_REQUEST)

    except (TypeError, ValueError, KeyError):
        return Response({
            'detail': '非法参数。'
        }, status=status.HTTP_400_BAD_REQUEST)

    meetingrooms = Meetingroom.objects.filter(**kwargs)

    resultset = {}
    for meetingroom in meetingrooms:
        result = {
            'id': meetingroom.id,
            'info': {
                'name': meetingroom.name,
                'location': meetingroom.location,
                'seats_count': meetingroom.seats_count,
                'label': meetingroom.label,
                'description': meetingroom.description
            },
            'choices': []
        }

        # generate timetable for each available meetingroom
        timetable = {}
        cur = target_from_time
        while cur <= target_to_time:
            timetable[cur] = True
            cur += unit

        reservations = meetingroom.reservations.filter(reserve_to__gt=target_from_time, reserve_from__lt=target_to_time).all()
        for reservation in reservations:
            cur = reservation.reserve_from
            while cur < reservation.reserve_to:
                timetable[cur] = False
                cur += unit
            timetable[reservation.reserve_from] = True
        
        # calculate available times of each meetingroom
        cur = target_from_time
        cnt = 0
        while cur <= target_to_time:
            if timetable[cur]:
                if cnt == length_minutes:
                    result['choices'].append((cur - timedelta(minutes=length_minutes), cur))
                    cnt = 5
                else:
                    cnt += 5
            else:
                cnt = 0
            cur += unit
        
        if result['choices']:
            if meetingroom.location not in resultset:
                resultset[meetingroom.location] = []
            resultset[meetingroom.location].append(result)

    def cmp_meetingrooms(a, b):
        if a['info']['seats_count'] == b['info']['seats_count']:
            return -1 if a['info']['name'] < b['info']['name'] else 1
        return -1 if a['info']['seats_count'] < b['info']['seats_count'] else 1

    resultset_final = []
    for location, meetingrooms in resultset.items():
        resultset_final.append({
            'location': location,
            'meetingrooms': sorted(meetingrooms, key=cmp_to_key(cmp_meetingrooms))
        })

    def cmp_resultset(a, b):
        if (a['meetingrooms'][0]['info']['seats_count'] == b['meetingrooms'][0]['info']['seats_count']):
            return -1 if a['location'] < b['location'] else 1
        return -1 if a['meetingrooms'][0]['info']['seats_count'] < b['meetingrooms'][0]['info']['seats_count'] else 1

    return Response(sorted(resultset_final, key=cmp_to_key(cmp_resultset)))

class ReservationViewset(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)