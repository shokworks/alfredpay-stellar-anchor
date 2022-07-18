from django.urls import path, include
from .views import generate_toml, MySEP10Auth, get_home
# from .sep6 import urls as sep6_urls
# from .sep24 import urls as sep24_urls



urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth2", MySEP10Auth.as_view()),
    path("TRANSFER_SERVER/", include("core.polaris.sep6.urls")),
    path("auth", include("core.polaris.sep10.urls")),
    # path("sep24/", include("core.polaris.sep24.urls")),
    # path("", get_home.as_view())
]