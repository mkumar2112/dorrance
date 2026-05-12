from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q
from .models import Role, PERMISSION_CHOICES



class DashboardView:
    def dashboard(request):
        return render(request, "dashboard.html")


class RoleView:
    def role_list(request):
        search = request.GET.get("search", "").strip()

        roles = Role.objects.filter(is_deleted=False)

        if search:
            roles = roles.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(display_name__icontains=search)
            )

        context = {
            "permission_choices": PERMISSION_CHOICES,
            "roles": roles,
            "search": search,
        }

        return render(request, "home/roles/layout.html", context)




        role = get_object_or_404(Role, pk=pk, is_deleted=False)

        role.is_deleted = True
        role.save(update_fields=["is_deleted"])

        messages.success(request, "Role deleted successfully.")

        return redirect("role_list")