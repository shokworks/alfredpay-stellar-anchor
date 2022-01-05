from django.urls import path

from core.dashboard.login.views import (
    LoginView, logoutAPIView,
    )


urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', logoutAPIView.as_view(), name='Logout'),
]
