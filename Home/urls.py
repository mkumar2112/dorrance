from django.urls import path
from .views import *

urlpatterns = [

    path("roles/", RoleView.role_list, name="role_list"),

    path("roles/create/", RoleView.role_list, name="role_create"),

    # path("roles/<int:pk>/update/", RoleView.role_update, name="role_update"),

    # path("roles/<int:pk>/delete/", RoleView.role_delete, name="role_delete"),

]


