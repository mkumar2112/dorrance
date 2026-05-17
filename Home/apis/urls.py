from django.urls import path, include

urlpatterns = [
    path("", include("Home.apis.roles.urls")),
    path("", include("Home.apis.users.urls")),
]