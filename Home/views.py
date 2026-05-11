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
            "roles": roles,
            "search": search,
        }

        return render(request, "home/roles/role_list.html", context)


    def role_create(request):

        if request.method == "POST":

            name = request.POST.get("name")
            display_name = request.POST.get("display_name")
            description = request.POST.get("description")

            permissions = request.POST.getlist("permissions")

            is_default = request.POST.get("is_default") == "on"
            is_active = request.POST.get("is_active") == "on"

            role = Role.objects.create(
                name=name,
                display_name=display_name,
                description=description,
                permissions=permissions,
                is_default=is_default,
                is_active=is_active,
            )

            messages.success(request, "Role created successfully.")
            return redirect("role_list")

        context = {
            "permissions": PERMISSION_CHOICES,
            "title": "Create Role"
        }

        return render(request, "home/roles/role_form.html", context)


    def role_update(request, pk):

        role = get_object_or_404(Role, pk=pk, is_deleted=False)

        if request.method == "POST":

            role.name = request.POST.get("name")
            role.display_name = request.POST.get("display_name")
            role.description = request.POST.get("description")

            role.permissions = request.POST.getlist("permissions")

            role.is_default = request.POST.get("is_default") == "on"
            role.is_active = request.POST.get("is_active") == "on"

            role.save()

            messages.success(request, "Role updated successfully.")
            return redirect("role_list")

        context = {
            "role": role,
            "permissions": PERMISSION_CHOICES,
            "title": "Update Role"
        }

        return render(request, "home/roles/role_form.html", context)


    def role_delete(request, pk):

        role = get_object_or_404(Role, pk=pk, is_deleted=False)

        role.is_deleted = True
        role.save(update_fields=["is_deleted"])

        messages.success(request, "Role deleted successfully.")

        return redirect("role_list")