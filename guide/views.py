from rest_framework import viewsets, permissions, status, filters, mixins
from rest_framework.response import Response
from guide.models import Guide, GuideCategory
from guide.serializers import GuideSerializer
from django.http import Http404, FileResponse
from django.utils.http import urlquote
from rest_framework.decorators import api_view, permission_classes
import os
from guide.tasks import send_guide_email

class GuideViewset(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = GuideSerializer
    queryset = Guide.objects.all()
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )

    def retrieve(self, request, pk):
        guide = self.get_object()
        file = guide.file
    
        try:
            fd = open(file.path, 'rb')
        except FileNotFoundError:
            raise Http404

        return FileResponse(fd)

@api_view(('POST', ))
@permission_classes((permissions.IsAuthenticated, ))
def email_guide(request, pk):
    email = request.user.email
    if not email:
        return Response({
            'detail': '您的账户尚未绑定邮箱。'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        guide = Guide.objects.get(pk=pk)
    except Guide.DoesNotExist:
        raise Http404
    
    send_guide_email.delay(guide.id, email)
    return Response()