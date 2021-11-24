from django.urls import path, include
from .views import generate_toml, MySEP10Auth

urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth", include("polaris.sep10.urls")),
    path("auth-old", MySEP10Auth.as_view()),
    path("sep24/", include("polaris.sep24.urls")),
]
