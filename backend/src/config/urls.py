from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
import core.testing.urls as testing_urls
# import polaris.urls


urlpatterns = [
    path("", include(testing_urls)),
    path('aYpTM6GvqdD2/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += [
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
