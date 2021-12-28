from django.conf import settings
from django.urls import path, include
from django.contrib import admin

import core.dashboard.myuser.urls as myuser_urls
import core.testing.urls as testing_urls
import core.dashboard.login.urls as login_urls


urlpatterns = [
    path("myuser/", include(myuser_urls)),
    path("", include(testing_urls)),
    path('', include(login_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]
