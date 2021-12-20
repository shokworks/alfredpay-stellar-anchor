from django.urls import path, include
from .views import generate_toml, MySEP10Auth
# from .sep6 import urls as sep6_urls
# from .sep24 import urls as sep24_urls

urlpatterns = [
    path(".well-known/stellar.toml", generate_toml),
    path("auth2", MySEP10Auth.as_view()),
    # path("auth", include("polaris.sep10.urls")),
    # path("sep24/", include("polaris.sep24.urls")),
    # path("sep24/", include(sep24_urls)),
    # path("sep6/", include(sep6_urls)),
]
