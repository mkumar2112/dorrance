from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from ...models import Organization, OrgAdmin, OrganizationGallery
from .serializers import OrganizationSerializer, OrgAdminSerializer, OrganizationGallerySerializer
from rest_framework.permissions import IsAuthenticated


import json
from django.http import JsonResponse


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Organization.objects.filter(is_deleted=False)

        name = self.request.query_params.get("name")
        city = self.request.query_params.get("city")
        state = self.request.query_params.get("state")
        country = self.request.query_params.get("country")
        is_active = self.request.query_params.get("is_active")
        is_verified = self.request.query_params.get("is_verified")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if state:
            queryset = queryset.filter(state__icontains=state)

        if country:
            queryset = queryset.filter(country__icontains=country)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == "true")

        return queryset.order_by("-id")

    # Uncomment the following method if you want to set the created_by field automatically when creating an organization
    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        organization = self.get_object()
        organization.is_deleted = True
        organization.is_active = False
        organization.save()

        return Response(
            {
                "status": True,
                "message": "Organization deleted successfully."
            },
            status=status.HTTP_200_OK
        )





def change_organization(request):
    if request.method == "POST":
        data = json.loads(request.body)

        org_id = data.get("organization_id")

        request.session["selected_org"] = org_id

        return JsonResponse({
            "status": True,
            "message": "Organization changed successfully"
        })

    return JsonResponse({
        "status": False,
        "message": "Invalid request"
    })


class OrgAdminViewSet(viewsets.ModelViewSet):
    serializer_class = OrgAdminSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OrgAdmin.objects.select_related(
            "user",
            "organization"
        ).filter(is_deleted=False)

        organization_id = self.request.query_params.get("organization_id")
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        return queryset.order_by("-id")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active"])

        return Response(
            {
                "status": True,
                "message": "Org admin deleted successfully"
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        organization_id = request.data.get("organization")

        deleted_org_admin = OrgAdmin.objects.filter(
            user_id=user_id,
            organization_id=organization_id,
            is_deleted=True,
        ).first()

        if deleted_org_admin:
            deleted_org_admin.is_deleted = False
            deleted_org_admin.is_active = True
            deleted_org_admin.save()

            serializer = self.get_serializer(deleted_org_admin)

            return Response(
                {
                    "status": True,
                    "message": "Org admin restored successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": True,
                "message": "Org admin created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": True,
                "message": "Org admin updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    


class OrganizationGalleryViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationGallerySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_selected_organization(self):
        organization_id = (
            self.request.session.get("selected_org")
            or self.request.query_params.get("organization_id")
            or self.request.data.get("organization_id")
            or self.request.headers.get("X-Organization-Id")
        )

        if not organization_id:
            return None

        return Organization.objects.filter(
            id=organization_id,
            is_deleted=False
        ).first()

    def get_queryset(self):
        queryset = OrganizationGallery.objects.filter(
            is_deleted=False
        ).select_related("organization")

        organization = self.get_selected_organization()

        if organization:
            queryset = queryset.filter(organization=organization)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        organization = self.get_selected_organization()

        if not organization:
            return Response(
                {
                    "success": False,
                    "message": "Organization is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(organization=organization)

            return Response(
                {
                    "success": True,
                    "message": "Gallery image added successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Gallery image updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        gallery = self.get_object()
        gallery.is_deleted = True
        gallery.is_active = False
        gallery.save()

        return Response(
            {
                "success": True,
                "message": "Gallery image deleted successfully"
            },
            status=status.HTTP_200_OK
        )


