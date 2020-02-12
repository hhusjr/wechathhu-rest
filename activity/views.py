from activity.models import Activity, Enrollment, ClockinMeta, ClockinRecord
from activity.serializers import ActivitySerializer, EnrollmentSerializer, ClockinSerializer
from rest_framework import permissions, viewsets, filters, views, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet
from django.db.models import Q
from django.db.models.aggregates import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import base64
import json
from activity.apps import ActivityConfig
from django.utils import timezone
from datetime import timedelta

class ActivityViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ActivitySerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )

    def get_queryset(self):
        filter_kwargs = {
            'open_for_enrollment': True
        }
        try:
            if self.request.query_params['my'].strip() == 'yes':
                # == 1
                filter_kwargs['my_enrollment_count__gt'] = 0
        except KeyError:
            pass
        
        annotate_kwargs = {
            'enrollment_count': Count('enrollments'),
            'my_enrollment_count': Count('enrollments', Q(enrollments__user=self.request.user))
        }
        return Activity.objects.annotate(**annotate_kwargs).filter(**filter_kwargs).order_by('-id')
        
class EnrollmentViewset(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).order_by('-enroll_time')

class ClockinViewset(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request):
        try:
            key = str(request.data['key'])
            data = base64.b64decode(key)
            data = json.loads(data)
            
            activity = Activity.objects.get(id=data['activity_id'])
            label = data['label']
            generated_key = data['generated_key']

            earliest = timezone.now() - timedelta(seconds=ActivityConfig.clockin_qrcode_expire)
            clockin_meta = ClockinMeta.objects.get(activity=activity, label=label, generated_key=generated_key)

            if clockin_meta.changed < earliest:
                return Response({
                    'detail': '打卡二维码已过期，请重试。'
                }, status=status.HTTP_400_BAD_REQUEST)

            now = timezone.now()
            if now < clockin_meta.from_time or now > clockin_meta.to_time:
                return Response({
                    'detail': '打卡时间不在指定的时间范围内。'
                }, status=status.HTTP_400_BAD_REQUEST)

            if clockin_meta.need_enrollment:
                if not Enrollment.objects.filter(activity=activity, user=request.user).count():
                    return Response({
                        'detail': '您尚未报名该活动，无法进行本次打卡。'
                    }, status=status.HTTP_400_BAD_REQUEST)

            record, created = ClockinRecord.objects.get_or_create(
                user=request.user,
                clockin_meta=clockin_meta
            )

            if not created:
                return Response({
                    'detail': '已存在该打卡记录。'
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'label': clockin_meta.label,
                'activity_name': clockin_meta.activity.name
            })
        except (KeyError, TypeError, json.JSONDecodeError, ClockinMeta.DoesNotExist):
            return Response({
                'detail': '打卡二维码异常或已过期，请重试。'
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return Response({
                'detail': '该活动不存在。'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = ClockinMeta.objects.filter(activity=activity).order_by('from_time', 'created')
        serializer = ClockinSerializer(queryset, many=True, context={
            'request': request
        })

        return Response(serializer.data)
