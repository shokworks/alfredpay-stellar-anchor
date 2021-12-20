from django.conf import settings
from django.urls import path, include
from django.contrib import admin
import core.polaris.urls
import core.testing.urls as testing_urls


urlpatterns = [
    # path("", include(polaris.urls))
    path("", include(testing_urls))
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]
