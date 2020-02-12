from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

TOKEN_LIFETIME = timedelta(hours=3)

def fetch_user_token(user):
    token, created = Token.objects.get_or_create(user=user)

    utc_now = timezone.now()
    if not created:
        if token.created < utc_now - TOKEN_LIFETIME:
            token.delete()
            token = Token.objects.create(user=user)
            created = True
        else:
            token.created = utc_now
            token.save(update_fields=['created'])

    return (token, created)

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        token_user, token = super().authenticate_credentials(key)

        utc_now = timezone.now()
        if token.created < utc_now - TOKEN_LIFETIME:
            raise AuthenticationFailed('Token has expired.')

        return (token_user, token)