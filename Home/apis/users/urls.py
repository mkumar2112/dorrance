from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginAPIView, RegisterAPIView, UserProfileViewSet
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

user_profile_router = DefaultRouter()
user_profile_router.register(r"user-profile", UserProfileViewSet, basename="user-profile")


urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("", include(user_profile_router.urls)),]