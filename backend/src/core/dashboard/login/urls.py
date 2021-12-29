from django.urls import path

# from dj_rest_auth.views import LoginView

from core.dashboard.login.views import (
    LoginView, AuthTokenGeneration, logoutAPIView,
    )


urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    # URLs that require a user to be logged in with a valid session / token.
    path('user/', AuthTokenGeneration.as_view(), name='rest_user_details'),
    path('logout/', logoutAPIView.as_view(), name='Logout'),
]
