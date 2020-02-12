from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from django.utils import timezone
from user.authentication import fetch_user_token

class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = fetch_user_token(user)
        return Response({
            'token': token.key
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()