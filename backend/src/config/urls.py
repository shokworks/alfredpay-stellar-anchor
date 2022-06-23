from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
import core.testing.urls as testing_urls
# import polaris.urls


urlpatterns = [
    path("", include(testing_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
