from django.urls import path, include

urlpatterns = [
    path("", include("Home.apis.roles.urls")),
]