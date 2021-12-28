from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import (
    RetrieveAPIView, RetrieveDestroyAPIView
    )
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.dashboard.login.serializers import MyUserTokenSerializer


class AuthTokenGeneration(RetrieveAPIView):
    """
    Reads UserModel and UserToken fields
    Accepts GET methods.
    Default display fields: user token, user id, username.
    """
    serializer_class = MyUserTokenSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        request_user = get_user_model().objects.filter(id=request.user.id)
        login_serializer = MyUserTokenSerializer(request.user)
        login_serializer2 = MyUserTokenSerializer(data=login_serializer.data)
        if login_serializer2.is_valid():
            token_user = request_user.first()
            token, created = Token.objects.get_or_create(user=token_user)
            if token.key:
                return Response({
                    'token': token.key,
                    'user': login_serializer.data,
                    'message': 'Login Successful!',
                    },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message':
                    'There is no token for that user at the moment!',
                    }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'error':'This user cannot log in.'
                }, status=status.HTTP_401_UNAUTHORIZED)


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
