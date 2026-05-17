from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...models import FoodCategory, Organization
from .serializers import FoodCategorySerializer


class FoodCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FoodCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_selected_organization(self):
        organization_id = self.request.session.get("selected_org")

        if not organization_id:
            return None

        return Organization.objects.filter(
            id=organization_id
        ).first()

    def get_queryset(self):
        organization = self.get_selected_organization()

        if not organization:
            return FoodCategory.objects.none()

        queryset = FoodCategory.objects.filter(
            organization=organization,
            is_deleted=False
        )

        search = self.request.query_params.get("search")
        is_active = self.request.query_params.get("is_active")

        if search:
            queryset = queryset.filter(name__icontains=search)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        return queryset.order_by("sort_order", "id")

    def list(self, request, *args, **kwargs):
        organization = self.get_selected_organization()

        if not organization:
            return Response(
                {
                    "status": False,
                    "message": "No organization selected"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "status": True,
                "message": "Food categories fetched successfully",
                "food_categories": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        organization = self.get_selected_organization()

        if not organization:
            return Response(
                {
                    "status": False,
                    "message": "No organization selected"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(
            {
                "status": True,
                "message": "Food category fetched successfully",
                "food_category": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        organization = self.get_selected_organization()

        if not organization:
            return Response(
                {
                    "status": False,
                    "message": "No organization selected"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(organization=organization)

        return Response(
            {
                "status": True,
                "message": "Food category created successfully",
                "food_category": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        organization = self.get_selected_organization()

        if not organization:
            return Response(
                {
                    "status": False,
                    "message": "No organization selected"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(organization=organization)

        return Response(
            {
                "status": True,
                "message": "Food category updated successfully",
                "food_category": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        organization = self.get_selected_organization()

        if not organization:
            return Response(
                {
                    "status": False,
                    "message": "No organization selected"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active"])

        return Response(
            {
                "status": True,
                "message": "Food category deleted successfully"
            },
            status=status.HTTP_200_OK
        )