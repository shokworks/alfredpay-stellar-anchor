from django.urls import path, include
from .views import generate_toml

urlpatterns = [path(".well-known/stellar.toml", generate_toml)]
