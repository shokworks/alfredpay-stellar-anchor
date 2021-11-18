from django.urls import path, include
from django.contrib import admin
import core.testing.urls as testing_urls
# import polaris.urls


urlpatterns = [
    # path("", include(polaris.urls))
    path('admin/', admin.site.urls),
    path("", include(testing_urls))
]
