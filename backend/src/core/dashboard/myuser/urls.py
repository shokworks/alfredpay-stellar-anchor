from django.urls import path

from .views import (
    AdminUserProfileListCreateAPIView as AdminUPListCreateAPIView,
    AdminUserProfileRetrieveUpdateDestroyAPIView as AdminUPDetailView,
    UserProfileListAPIView as UPListView,
    UserProfileRetrieveUpdateAPIView as UPDetailView,
    )


urlpatterns = [
    path("Admin_UP/", AdminUPListCreateAPIView.as_view(),
        name="Admin_List_User&Profile"
        ),
    path("Admin_UP/<int:pk>/", AdminUPDetailView.as_view(),
        name="Admin_Detail_User&Profile"
        ),
    path("profile/", UPListView.as_view(),
        name="UserProfile"
        ),
    path("profile/<int:pk>/", UPDetailView.as_view(),
        name="UserProfileDetail"
        )
]
