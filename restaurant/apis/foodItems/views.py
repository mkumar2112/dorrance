from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...models import FoodItem, Organization
from .serializers import FoodItemSerializer


class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]

    def get_selected_organization(self):
        organization_id = self.request.session.get("selected_org")

        if not organization_id:
            return None

        return Organization.objects.filter(id=organization_id).first()

    def get_queryset(self):
        organization = self.get_selected_organization()

        if not organization:
            return FoodItem.objects.none()

        queryset = FoodItem.objects.select_related(
            "organization",
            "category",
            "created_by"
        ).filter(
            organization=organization,
            is_deleted=False
        )

        search = self.request.query_params.get("search")
        category_id = self.request.query_params.get("category_id")
        is_active = self.request.query_params.get("is_active")
        is_available = self.request.query_params.get("is_available")
        is_featured = self.request.query_params.get("is_featured")
        is_veg = self.request.query_params.get("is_veg")
        is_spicy = self.request.query_params.get("is_spicy")

        if search:
            queryset = queryset.filter(name__icontains=search)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        if is_available in ["true", "false"]:
            queryset = queryset.filter(is_available=is_available == "true")

        if is_featured in ["true", "false"]:
            queryset = queryset.filter(is_featured=is_featured == "true")

        if is_veg in ["true", "false"]:
            queryset = queryset.filter(is_veg=is_veg == "true")

        if is_spicy in ["true", "false"]:
            queryset = queryset.filter(is_spicy=is_spicy == "true")

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
                "message": "Food items fetched successfully",
                "food_items": serializer.data
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
                "message": "Food item fetched successfully",
                "food_item": serializer.data
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

        serializer.save(
            organization=organization,
            created_by=request.user
        )

        return Response(
            {
                "status": True,
                "message": "Food item created successfully",
                "food_item": serializer.data
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
                "message": "Food item updated successfully",
                "food_item": serializer.data
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
        instance.is_available = False
        instance.save(
            update_fields=[
                "is_deleted",
                "is_active",
                "is_available"
            ]
        )

        return Response(
            {
                "status": True,
                "message": "Food item deleted successfully"
            },
            status=status.HTTP_200_OK
        )