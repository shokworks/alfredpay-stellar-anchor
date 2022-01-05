from django.conf import settings
from django.contrib.auth import (
    get_user_model, login as django_login
)
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    GenericAPIView, RetrieveDestroyAPIView
    )
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from dj_rest_auth.app_settings import (
    JWTSerializer, JWTSerializerWithExpiration, LoginSerializer,
    TokenSerializer, create_token
)
from dj_rest_auth.models import get_token_model
from dj_rest_auth.utils import jwt_encode

from core.dashboard.login.serializers import MyUserTokenSerializer

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2',
    ),
)


class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token if the credentials are
    valid and authenticated. Calls Django Auth login method to register User ID
    in Django session framework.
    Accept the following POST parameters: username, email, password.
    Return the REST Framework Token Object's key.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_scope = 'dj_rest_auth'

    user = None
    access_token = None
    token = None

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):

            if getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False):
                response_serializer = JWTSerializerWithExpiration
            else:
                response_serializer = JWTSerializer

        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        token_model = get_token_model()

        if getattr(settings, 'REST_USE_JWT', False):
            self.access_token, self.refresh_token = jwt_encode(self.user)
        elif token_model:
            self.token = create_token(token_model, self.user, self.serializer)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_simplejwt.settings import (
                api_settings as jwt_settings,
            )
            access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            refresh_token_expiration = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
            return_expiration_times = getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False)

            data = {
                'user': self.user,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
            }

            if return_expiration_times:
                data['access_token_expiration'] = access_token_expiration
                data['refresh_token_expiration'] = refresh_token_expiration

            serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context(),
            )
        elif self.token:
            serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context(),
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

        response = Response(serializer.data, status=status.HTTP_200_OK)
        if getattr(settings, 'REST_USE_JWT', False):
            from .jwt_auth import set_jwt_cookies
            set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response

    def get(self, request, *args, **kwargs):
        request_user = get_user_model().objects.filter(id=request.user.id)
        if not request_user:
            return Response({
                'message': 'Come to the DarkSide we have Cookies!',
            },status=status.HTTP_204_NO_CONTENT)

        login_serializer = MyUserTokenSerializer(request.user)
        login_serializer2 = MyUserTokenSerializer(data=login_serializer.data)
        if login_serializer2.is_valid():
            token_user = request_user.first()
            token, created = Token.objects.get_or_create(user=token_user)
            return Response({
                'token': token.key,
                'user': login_serializer.data,
                'message': 'Login Successful!',
                },status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error':'This user cannot log in.'
                }, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


def Delete_Session(user_id):
    datetimenow = timezone.now()
    all_sessions = Session.objects.filter(expire_date__gte=datetimenow)
    if all_sessions.exists():
        for session in all_sessions:
            session_data = session.get_decoded()
            if user_id == int(session_data.get('_auth_user_id')):
                session.delete()
                delete_sessions = True
            return delete_sessions


class logoutAPIView(RetrieveDestroyAPIView):
    """
    Calls Django logout method and delete the Token object and
    all the Sessions assigned to the current User object.

    Accepts GET, DELETE methods.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args,**kwargs):
        request_user = get_user_model().objects.filter(id=request.user.id)
        token_user = request_user.first()
        try:
            token = Token.objects.get(user=token_user)
            login_serializer = MyUserTokenSerializer(request.user)
            login_serializer2 = MyUserTokenSerializer(
                data=login_serializer.data
                )
            if login_serializer2.is_valid():
                return Response({
                    'token': token.key,'user': login_serializer.data,
                    'message': 'Authenticated User and with Token'
                    }, status=status.HTTP_200_OK)
            return Response({
                'A User with those credentials was not found!'
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                'message': 'User does not have Token!'
                },status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        request_user = get_user_model().objects.filter(
            id=request.user.id
            ).first()
        token = Token.objects.get(user=request_user)
        token.delete()
        token_message = 'Deleted User Token!'
        if Delete_Session(request.user.id):
            session_message = 'Deleted User Sessions!'
        else:
            session_message = 'User still have Sessions Open!'
        return Response({
            'token_message':token_message, 'session_message':session_message
            }, status=status.HTTP_200_OK)
