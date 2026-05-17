from django.urls import path
from .views import *

urlpatterns = [

    path("roles/", RoleView.role_list, name="role_list"),
    path("users/", UserView.user_list, name="user_list"),

]


urlpatterns += [

    path("login/", AuthView.login, name="login"),
    path("logout/", AuthView.logout_view, name="logout"),

]


