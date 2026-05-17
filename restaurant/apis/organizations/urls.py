from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organizations")

org_admin_router = DefaultRouter()
org_admin_router.register(r"org-admins", OrgAdminViewSet, basename="org-admins")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(org_admin_router.urls)),
    path( "change-organization/", change_organization, name="change_organization"),
]





