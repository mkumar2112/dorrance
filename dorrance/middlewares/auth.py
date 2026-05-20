from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        exempt_urls = [
            reverse("login"),
            reverse("logout"),
            "/api/login/",
            "/api/register/",
            "/api/token/refresh/",
            "/admin/login/",
        ]

        exempt_prefixes = [
            "/static/",
            "/media/",
            "/admin/",
            "/api/",
        ]

        for prefix in exempt_prefixes:
            if request.path.startswith(prefix):
                return self.get_response(request)

        if request.path in exempt_urls:
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("login")

        response = self.get_response(request)

        return response