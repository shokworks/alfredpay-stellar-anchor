from django.urls import path, include, re_path

from core.polaris import settings


urlpatterns = []
if "sep-1" in settings.ACTIVE_SEPS:
    urlpatterns.append(path(".well-known/", include("core.polaris.sep1.urls")))

if "sep-6" in settings.ACTIVE_SEPS:
    urlpatterns.append(path("sep6/", include("core.polaris.sep6.urls")))

if "sep-10" in settings.ACTIVE_SEPS:
    urlpatterns.append(re_path(r"^auth/?", include("core.polaris.sep10.urls")))

if "sep-12" in settings.ACTIVE_SEPS:
    urlpatterns.append(path("kyc/", include("core.polaris.sep12.urls")))

if "sep-24" in settings.ACTIVE_SEPS:
    urlpatterns.append(path("sep24/", include("core.polaris.sep24.urls")))

if "sep-31" in settings.ACTIVE_SEPS:
    urlpatterns.append(path("sep31/", include("core.polaris.sep31.urls")))

if "sep-38" in settings.ACTIVE_SEPS:
    urlpatterns.append(path("sep38/", include("core.polaris.sep38.urls")))
