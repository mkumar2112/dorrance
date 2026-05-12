from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Role
from .serializers import RoleSerializer


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer

    def get_queryset(self):
        queryset = Role.objects.filter(is_deleted=False)

        is_active = self.request.query_params.get("is_active")
        name = self.request.query_params.get("name")
        slug = self.request.query_params.get("slug")

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if slug:
            queryset = queryset.filter(slug__icontains=slug)

        return queryset.order_by("id")

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        role.is_deleted = True
        role.is_active = False
        role.save()

        return Response(
            {"message": "Role deleted successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def check_permission(self, request, pk=None):
        role = self.get_object()
        permission_slug = request.data.get("permission")

        if not permission_slug:
            return Response(
                {"error": "Permission is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "role": role.name,
            "permission": permission_slug,
            "has_permission": role.has_permission(permission_slug)
        })