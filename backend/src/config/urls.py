from django.urls import path, include
from django.contrib import admin
import polaris.urls
import core.testing.urls as testing_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    # path("", include(polaris.urls))
    path("", include(testing_urls))
]
