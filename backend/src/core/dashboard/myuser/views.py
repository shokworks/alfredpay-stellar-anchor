from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.dashboard.login.authentication_mixin import Authentication
from core.dashboard.myuser.serializers import (
    AdminUserProfileSerializer, UserProfileSerializer
    )


class AdminUserProfileListCreateAPIView(
    Authentication,
    generics.ListCreateAPIView
    ):
    permission_classes = (IsAdminUser, )
    serializer_class = AdminUserProfileSerializer

    def get_queryset(self):
        return self.get_serializer().Meta.model.objects.all()


class AdminUserProfileRetrieveUpdateDestroyAPIView(
    Authentication,
    generics.RetrieveUpdateDestroyAPIView
    ):
    serializer_class = AdminUserProfileSerializer

    def get_queryset(self):
        return self.get_serializer().Meta.model.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = get_user_model().objects.all().filter(
            username=instance
            ).values().first()
        newuser = User.objects.get(username=user['username'])
        newuser.is_active = False
        newuser.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileListAPIView(
    Authentication, generics.ListAPIView
    ):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return self.get_serializer(
            ).Meta.model.objects.filter(username=self.request.user)


class UserProfileRetrieveUpdateAPIView(
    Authentication, generics.RetrieveUpdateAPIView
    ):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return self.get_serializer(
            ).Meta.model.objects.filter(username=self.request.user)
