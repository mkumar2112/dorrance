from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from restaurant.models import Organization


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


from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

class AuthView:

    @staticmethod
    def login(request):

        if request.method == "POST":

            mobile_number = request.POST.get("mobile_number")
            password = request.POST.get("password")

            try:
                user = User.objects.get(
                    mobile_number=mobile_number
                )

                if user.check_password(password):

                    login(request, user)

                    messages.success(
                        request,
                        "Login successful"
                    )

                    return redirect("/")

                else:
                    messages.error(
                        request,
                        "Invalid password"
                    )

            except User.DoesNotExist:

                messages.error(
                    request,
                    "User not found"
                )

        return render(
            request,
            "account/login.html"
        )
    

    def logout_view(request):
        logout(request)
        return redirect("login")

        