from django.conf import settings
from django.urls import path, include
from .views import generate_toml, MySEP10Auth, get_home
from django.contrib import admin
# from .sep6 import urls as sep6_urls
# from .sep24 import urls as sep24_urls



urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth2", MySEP10Auth.as_view()),
    path("sep6/", include("core.polaris.sep6.urls")),
    path("auth", include("core.polaris.sep10.urls")),
    path("sep24/", include("core.polaris.sep24.urls")),
    path("", get_home.as_view())
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

