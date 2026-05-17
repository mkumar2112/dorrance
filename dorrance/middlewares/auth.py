from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # URLs that don't require login
        exempt_urls = [
            reverse("login"),
            reverse("logout"),
        ]

        # Allow static/media files
        if (
            request.path.startswith("/static/")
            or request.path.startswith("/media/")
        ):
            return self.get_response(request)

        # If user not logged in
        if not request.user.is_authenticated:

            # Allow exempt URLs
            if request.path not in exempt_urls:
                return redirect("login")

        response = self.get_response(request)

        return response