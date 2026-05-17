from django.contrib.auth import logout
from django.shortcuts import redirect
from restaurant.models import Organization, OrgAdmin


def organization_context(request):
    org_list = Organization.objects.none()
    selected_org = None

    if not request.user.is_authenticated:
        return {
            "org_list": org_list,
            "selected_org": selected_org,
        }

    # Superuser can see all organizations
    if request.user.is_superuser:
        org_list = Organization.objects.filter(
            is_active=True,
            is_deleted=False
        )
    else:
        # Normal user can see only assigned admin organizations
        org_list = Organization.objects.filter(
            admins__user=request.user,
            admins__is_active=True,
            admins__is_deleted=False,
            is_active=True,
            is_deleted=False,
        ).distinct()

    # If user has no organization, logout
    if not org_list.exists():
        logout(request)
        request.session.flush()

        return {
            "org_list": Organization.objects.none(),
            "selected_org": None,
        }

    selected_org = request.session.get("selected_org")

    # If selected org not in allowed org list, select first org
    if not selected_org or not org_list.filter(id=selected_org).exists():
        first_org = org_list.first()

        selected_org = first_org.id
        request.session["selected_org"] = selected_org

    return {
        "org_list": org_list,
        "selected_org": str(selected_org),
    }
