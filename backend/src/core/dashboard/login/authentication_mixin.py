from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from core.dashboard.login.authentication import ExpiringTokenAuthentication
from core.dashboard.login.views import Delete_Session


class Authentication(object):
    def get_user(self, request):
        token = get_authorization_header(request).split()
        if token:
            try:
                token = token[1].decode()
            except:
                return None

            token_expire = ExpiringTokenAuthentication()
            message, token, user = token_expire.authenticate_credentials(token)
            if message == 'Su Token is Expired!':
                token.delete()
                Delete_Session(token.user.id)
                return message
            if token != None and user != None:
                return user
            return message
        return None

    def dispatch(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user == 'Your Token Has Expired!':
            session_message = 'Deleted User Sessions!'
            token_message = 'Your Token Has Expired!'
            responde = Response({
                'token_message':token_message,
                'session_message':session_message
                },status=status.HTTP_401_UNAUTHORIZED)
            responde.accepted_renderer = JSONRenderer()
            responde.accepted_media_type = 'application/json'
            responde.renderer_context = {}
            return responde
        if user is not None:
            if type(user) == str:
                responde = Response({'error': user},
                    status=status.HTTP_401_UNAUTHORIZED)
                responde.accepted_renderer = JSONRenderer()
                responde.accepted_media_type = 'application/json'
                responde.renderer_context = {}
                return responde
            return super().dispatch(request, *args, **kwargs)
        responde = Response({
            'error': 'Credentials have not been sent!'
            },status=status.HTTP_400_BAD_REQUEST)
        responde.accepted_renderer = JSONRenderer()
        responde.accepted_media_type = 'application/json'
        responde.renderer_context = {}
        return responde
