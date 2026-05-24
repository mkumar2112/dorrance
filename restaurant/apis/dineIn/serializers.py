from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ...models import DineInTable, DineInBooking

class DineInTableSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = DineInTable
        fields = [
            "id",
            "organization",
            "organization_name",
            "table_code",
            "table_name",
            "capacity",
            "floor",
            "section",
            "is_active",
            "is_deleted",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "organization_name",
            "is_deleted",
            "created_at",
            "updated_at",
        ]


class DineInBookingSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    table_code = serializers.CharField(source="table.table_code", read_only=True)
    table_name = serializers.CharField(source="table.table_name", read_only=True)
    table_capacity = serializers.IntegerField(source="table.capacity", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = DineInBooking
        fields = [
            "id",
            "organization",
            "organization_name",
            "user",
            "user_name",
            "table",
            "table_code",
            "table_name",
            "table_capacity",
            "booking_number",
            "booking_date",
            "booking_time",
            "no_of_people",
            "customer_name",
            "customer_mobile",
            "special_request",
            "status",
            "confirmed_at",
            "completed_at",
            "cancelled_at",
            "cancel_reason",
            "rejection_reason",
            "is_walk_in",
            "created_by",
            "created_by_name",
            "is_active",
            "is_deleted",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "organization",
            "organization_name",
            "booking_number",
            "created_by",
            "created_by_name",
            "confirmed_at",
            "completed_at",
            "cancelled_at",
            "is_deleted",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        from .views import get_selected_organization_id

        organization_id = get_selected_organization_id(request)

        if not organization_id:
            raise serializers.ValidationError({
                "organization": "Organization is not selected."
            })

        table = attrs.get("table")
        no_of_people = attrs.get("no_of_people")
        booking_date = attrs.get("booking_date")
        booking_time = attrs.get("booking_time")
        status_value = attrs.get("status")

        if self.instance:
            table = table if table is not None else self.instance.table
            no_of_people = no_of_people if no_of_people is not None else self.instance.no_of_people
            booking_date = booking_date if booking_date is not None else self.instance.booking_date
            booking_time = booking_time if booking_time is not None else self.instance.booking_time
            status_value = status_value if status_value is not None else self.instance.status

        if table:
            if str(table.organization_id) != str(organization_id):
                raise serializers.ValidationError({
                    "message": "Selected table does not belong to this organization."
                })

            if no_of_people and no_of_people > table.capacity:
                raise serializers.ValidationError({
                    "message": f"This table capacity is only {table.capacity} people."
                })

            already_booked = DineInBooking.objects.filter(
                organization_id=organization_id,
                table=table,
                booking_date=booking_date,
                booking_time=booking_time,
                status__in=["pending", "confirmed"],
                is_deleted=False,
            )

            if self.instance:
                already_booked = already_booked.exclude(pk=self.instance.pk)

            if already_booked.exists():
                raise serializers.ValidationError({
                    "message": "This table is already booked for this date and time."
                })

        if status_value == "cancelled":
            cancel_reason = attrs.get("cancel_reason")
            if self.instance and cancel_reason is None:
                cancel_reason = self.instance.cancel_reason

            if not cancel_reason:
                raise serializers.ValidationError({
                    "message": "Cancel reason is required when booking is cancelled."
                })

        if status_value == "rejected":
            rejection_reason = attrs.get("rejection_reason")
            if self.instance and rejection_reason is None:
                rejection_reason = self.instance.rejection_reason

            if not rejection_reason:
                raise serializers.ValidationError({
                    "message": "Rejection reason is required when booking is rejected."
                })

        return attrs
