<<<<<<< HEAD
from django.conf import settings
from django.urls import path, include
from django.contrib import admin
import polaris.urls

from .views import generate_toml, MySEP10Auth


urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth", include("polaris.sep10.urls")),
    path("auth2", MySEP10Auth.as_view()),
    path("sep24/", include("polaris.sep24.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

=======
from django.urls import path, include
from .views import generate_toml, MySEP10Auth

urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth", MySEP10Auth.as_view()),
    path("sep24/", include("polaris.sep24.urls")),
]
>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
