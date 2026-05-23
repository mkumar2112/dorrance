from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DineInTableViewSet, DineInBookingViewSet

router = DefaultRouter()

router.register(r"dinein-tables", DineInTableViewSet, basename="dinein-table")
router.register(r"dinein-bookings", DineInBookingViewSet, basename="dinein-booking")

urlpatterns = [
    path("", include(router.urls)),
]