from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...models import DineInTable, DineInBooking
from .serializers import DineInTableSerializer, DineInBookingSerializer

from django.core.exceptions import ValidationError as DjangoValidationError


def get_selected_organization_id(request):
    return (
        request.session.get("selected_org")
        or request.headers.get("X-Organization-Id")
        or request.query_params.get("organization_id")
        or request.data.get("organization_id")
    )


class DineInTableViewSet(viewsets.ModelViewSet):
    serializer_class = DineInTableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DineInTable.objects.filter(is_deleted=False)

        organization_id = get_selected_organization_id(self.request)
        table_code = self.request.query_params.get("table_code")
        is_active = self.request.query_params.get("is_active")

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        if table_code:
            queryset = queryset.filter(table_code__icontains=table_code)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        return queryset.order_by("id")

    def perform_create(self, serializer):
        organization_id = get_selected_organization_id(self.request)

        if not organization_id:
            raise ValueError("Organization is not selected in session")

        serializer.save(organization_id=organization_id)

    def perform_update(self, serializer):
        organization_id = get_selected_organization_id(self.request)

        if not organization_id:
            raise ValueError("Organization is not selected in session")

        serializer.save(organization_id=organization_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active", "updated_at"])

        return Response(
            {"success": True, "message": "Table deleted successfully"},
            status=status.HTTP_200_OK,
        )


class DineInBookingViewSet(viewsets.ModelViewSet):
    serializer_class = DineInBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DineInBooking.objects.filter(is_deleted=False).select_related(
            "organization", "table", "user", "created_by"
        )

        organization_id = get_selected_organization_id(self.request)
        table_id = self.request.query_params.get("table")
        status_value = self.request.query_params.get("status")
        booking_date = self.request.query_params.get("booking_date")
        customer_mobile = self.request.query_params.get("customer_mobile")
        booking_number = self.request.query_params.get("booking_number")

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        if table_id:
            queryset = queryset.filter(table_id=table_id)

        if status_value:
            queryset = queryset.filter(status=status_value)

        if booking_date:
            queryset = queryset.filter(booking_date=booking_date)

        if customer_mobile:
            queryset = queryset.filter(customer_mobile__icontains=customer_mobile)

        if booking_number:
            queryset = queryset.filter(booking_number__icontains=booking_number)

        return queryset.order_by("-id")

    def handle_exception(self, exc):
        if isinstance(exc, DjangoValidationError):
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": self.format_django_error(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().handle_exception(exc)

    def format_django_error(self, error):
        if hasattr(error, "message_dict"):
            return error.message_dict

        if hasattr(error, "messages"):
            return {"detail": error.messages}

        return {"detail": str(error)}

    def perform_create(self, serializer):
        organization_id = get_selected_organization_id(self.request)

        if not organization_id:
            raise serializers.ValidationError({
                "organization": "Organization is not selected."
            })

        serializer.save(
            organization_id=organization_id,
            created_by=self.request.user,
            user=serializer.validated_data.get("user") or self.request.user,
        )

    def perform_update(self, serializer):
        organization_id = get_selected_organization_id(self.request)

        if not organization_id:
            raise serializers.ValidationError({
                "organization": "Organization is not selected."
            })

        serializer.save(organization_id=organization_id)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response(
            {
                "success": True,
                "message": "Booking created successfully",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status

        response = super().update(request, *args, **kwargs)

        instance.refresh_from_db()

        if old_status != instance.status:
            now = timezone.now()
            update_fields = ["updated_at"]

            if instance.status == "confirmed" and not instance.confirmed_at:
                instance.confirmed_at = now
                update_fields.append("confirmed_at")

            elif instance.status == "completed" and not instance.completed_at:
                instance.completed_at = now
                update_fields.append("completed_at")

            elif instance.status == "cancelled" and not instance.cancelled_at:
                instance.cancelled_at = now
                update_fields.append("cancelled_at")

            instance.save(update_fields=update_fields)

        serializer = self.get_serializer(instance)

        return Response(
            {
                "success": True,
                "message": "Booking updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Booking deleted successfully",
            },
            status=status.HTTP_200_OK,
        )




