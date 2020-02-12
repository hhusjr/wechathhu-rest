from rest_framework import viewsets, mixins, permissions
from repair.models import RepairRequest, FaultCategory
from repair.serializers import RepairRequestSerializer, FaultCategorySerializer, RepairRequestViewSerializer
from django.core.mail import send_mass_mail
from repair.tasks import send_notification_email
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

class RepairRequestViewset(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'list':
            return RepairRequestViewSerializer
        return RepairRequestSerializer

    def get_queryset(self):
        return RepairRequest.objects.filter(user=self.request.user).all()

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)

        send_notification_email.delay(instance.id)

@api_view(('GET', ))
@permission_classes((permissions.IsAuthenticated, ))
def get_categories(request):
    queryset = FaultCategory.objects.all()
    serializer = FaultCategorySerializer(queryset, many=True)
    return Response(serializer.data)