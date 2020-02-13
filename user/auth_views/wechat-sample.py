from rest_framework import permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from user.models import User
from user.authentication import fetch_user_token
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from user.serializers import UserSerializer
import requests

class WechatApiConfig:
    app_id = 'wx398da70b27188a31'
    app_secret = '14b4d3eb035446559e61ce035f12a35d'
    router = {
        'code2session': 'https://api.weixin.qq.com/sns/jscode2session'
    }

class WechatAuthParamError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wechat Auth Param Error.'
    default_code = 'wechatauth_error'

def code2session(code):
    url = WechatApiConfig.router['code2session']
    res = requests.get(url, params={
        'appid': WechatApiConfig.app_id,
        'secret': WechatApiConfig.app_secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }).json()
    if 'openid' not in res:
        raise WechatAuthParamError('Cannot convert Wechat JSCode to session, maybe the code is wrong.')
    return res

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def code2token(request):
    try:
        code = request.data['code']
    except KeyError:
        raise WechatAuthParamError('Wechat JSCode field is required.')
    res = code2session(code)

    try:
        user = User.objects.get(wechat_open_id=res['openid'])
    except User.DoesNotExist:
        raise WechatAuthParamError('The user account has not been associated with Wechat account, you have to call API wechat-bind-wechat-user first.')
    
    token, created = fetch_user_token(user)
    return Response({
        'token': token.key
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class WechatAuthView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            code = request.data['code']
        except KeyError:
            raise WechatAuthParamError('Wechat JSCode field is required.')
        res = code2session(code)

        user = request.user
        user.wechat_open_id = res['openid']
        user.save(update_fields=['wechat_open_id'])

        serializer = UserSerializer(request.user, context={
            'request': request
        })

        return Response(serializer.data)

    def delete(self, request):
        user = request.user

        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            pass

        user.wechat_open_id = None
        user.save(update_fields=['wechat_open_id'])

        serializer = UserSerializer(request.user, context={
            'request': request
        })

        return Response(serializer.data)

wechat_auth_view = WechatAuthView.as_view()