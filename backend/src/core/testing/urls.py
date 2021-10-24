from django.urls import path, include
from .views import generate_toml, MySEP10Auth

urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth", MySEP10Auth.as_view())
]
