from reservation.models import Meetingroom, Reservation
from rest_framework import views, status, permissions, mixins, generics, viewsets
from rest_framework.viewsets import GenericViewSet
from datetime import timedelta
import datetime
from dateutil import parser
from django.utils import timezone
from rest_framework.response import Response
from reservation.serializers import ReservationSerializer, MeetingroomSerializer
import pytz
from functools import cmp_to_key
from rest_framework.decorators import api_view, permission_classes
from user.models import UserMeta

@api_view(('GET', ))
@permission_classes((permissions.IsAuthenticated, ))
def available_meetingrooms(request):
    try:
        query_from = parser.parse(request.query_params['query_from'])
        query_to = parser.parse(request.query_params['query_to'])
    except (KeyError, ValueError):
        return Response({
            'detail': '查询的开始和结束时间必须以正确格式给定。'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        people_count = int(request.query_params.get('people_count', 0))
    except (ValueError, TypeError):
        people_count = 0

    meetingrooms = Meetingroom.objects.filter(seats_count__gte=people_count).order_by('seats_count').all()    

    meetingrooms_display = []
    for meetingroom in meetingrooms:
        reservations = Reservation.objects.filter(meetingroom=meetingroom, reserve_from__gte=query_from, reserve_to__lte=query_to)
        reservations_display = []
        for reservation in reservations:
            try:
                contact = reservation.user.meta.phone
            except UserMeta.DoesNotExist:
                contact = None
            reservations_display.append({
                'time_range': (reservation.reserve_from, reservation.reserve_to),
                'reserve_user': str(reservation.user),
                'contact': contact,
                'description': reservation.description
            })
        meetingrooms_display.append({
            'reservations': reservations_display,
            'meetingroom': MeetingroomSerializer(meetingroom).data
        })
    
    return Response(meetingrooms_display)

class ReservationViewset(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, reserve_to__gte=timezone.now()).all()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)