from django.urls import path, include
from django.contrib import admin
import polaris.urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(polaris.urls))
]
