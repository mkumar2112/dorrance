from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from restaurant.models import Organization

from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken



class DashboardView:
    def dashboard(request):

        return render(request, "dashboard.html" )


class RoleView:
    def role_list(request):
        permission_choices = PERMISSION_CHOICES
        return render(request, "home/roles/layout.html", {
            "permission_choices": permission_choices,
        })




class UserView:
    def user_list(request):
        return render(request, "home/users/layout.html")



class AuthView:

    @staticmethod
    def login(request):

        if request.method == "POST":

            mobile_number = request.POST.get("mobile_number")
            password = request.POST.get("password")

            try:
                user = User.objects.get(mobile_number=mobile_number)

                if user.is_blocked:
                    messages.error(request, "Your account is blocked")
                    return redirect("/login/")

                if user.is_deleted:
                    messages.error(request, "Your account is deleted")
                    return redirect("/login/")

                if not user.is_active:
                    messages.error(request, "Your account is inactive")
                    return redirect("/login/")

                if user.check_password(password):

                    login(request, user)

                    user.last_login = timezone.now()
                    user.last_login_ip = AuthView.get_client_ip(request)
                    user.last_login_device = request.META.get("HTTP_USER_AGENT", "")
                    user.save(update_fields=[
                        "last_login",
                        "last_login_ip",
                        "last_login_device"
                    ])

                    refresh = RefreshToken.for_user(user)

                    request.session["access_token"] = str(refresh.access_token)
                    request.session["refresh_token"] = str(refresh)

                    messages.success(request, "Login successful")

                    return redirect("/")

                else:
                    messages.error(request, "Invalid password")

            except User.DoesNotExist:
                messages.error(request, "User not found")

        return render(request, "account/login.html")

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]

        return request.META.get("REMOTE_ADDR")



    def logout_view(request):
        logout(request)
        return redirect("login")

        