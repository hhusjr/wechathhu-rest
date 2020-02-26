from user.models import User, UserMeta, Contact, Department
from rest_framework import viewsets, permissions, views, status, filters, mixins, generics
from user.serializers import UserSerializer, UserUpdateSerializer, UserChangePasswordSerializer, UserMetaSerializer, DepartmentSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models.functions import Concat
from django.db.models import Q
from django.http import Http404

class DepartmentViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = DepartmentSerializer
    pagination_class = None
    queryset = Department.objects.all()

class ContactViewset(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserMetaSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('fullname', 'post', 'user__department__name', 'qq', 'tel', 'phone')

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        res = sorted(serializer.data, key=lambda item: item['alpha'])
        return Response(res)

    def get_queryset(self):
        if self.request.query_params.get('my', 'no').strip() == 'yes':
            friends = self.request.user.contacts.values('friend_user')
            cond = Q(user__in=friends)
            try:
                if self.request.user.department is not None:
                    cond |= Q(user__department=self.request.user.department)
            except User.DoesNotExist:
                pass
            queryset = UserMeta.objects.filter(cond)
        else:
            queryset = UserMeta.objects
        return queryset.annotate(fullname=Concat('user__last_name', 'user__first_name')).all()

@api_view(('POST', 'DELETE'))
@permission_classes((permissions.IsAuthenticated, ))
def friend(request, pk):
    user = request.user
    
    try:
        friend_user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        contact, created = Contact.objects.get_or_create(
            user=user,
            friend_user=friend_user
        )
        if not created:
            return Response({
                'detail': '已存在该好友关系。'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response()
    
    if request.method == 'DELETE':
        try:
            contact = Contact.objects.get(user=user, friend_user=friend_user)
        except Contact.DoesNotExist:
            raise Http404
        contact.delete()
        return Response()

class CurrentUserView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        serializer = UserSerializer(request.user, context={
            'request': request
        })
        return Response(serializer.data)
        
    def put(self, request):
        errors = {}

        serializer_info = UserUpdateSerializer(request.user, data=request.data, context={
            'request': request
        })
        if not serializer_info.is_valid():
            errors.update(serializer_info.errors)

        changed_password = False
        if 'password' in request.data:
            changed_password = True
            serializer_password = UserChangePasswordSerializer(request.user, data=request.data)
            if not serializer_password.is_valid():
                errors.update(serializer_password.errors)
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        serializer_info.save()
        if changed_password:
            serializer_password.save()

        serializer = UserSerializer(request.user, context={
            'request': request
        })
        return Response(serializer.data)

current_user_view = CurrentUserView.as_view()

class CurrentUserMetaView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        meta, created = UserMeta.objects.get_or_create(user=self.request.user)
        return meta

    def get(self, request):
        meta = self.get_object()
        serializer = UserMetaSerializer(meta, context={
            'request': request
        })
        return Response(serializer.data)
        
    def put(self, request):
        meta = self.get_object()
        serializer = UserMetaSerializer(meta, data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

current_usermeta_view = CurrentUserMetaView.as_view()