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
        instance = DineInBooking(**attrs)

        if self.instance:
            for field, value in attrs.items():
                setattr(self.instance, field, value)
            instance = self.instance

        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict if hasattr(e, "message_dict") else e.messages
            )

        return attrs