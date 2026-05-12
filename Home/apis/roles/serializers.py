from rest_framework import serializers
from ...models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "display_name",
            "description",
            "permissions",
            "is_default",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate_permissions(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Permissions must be a list.")

        for permission in value:
            if not isinstance(permission, str):
                raise serializers.ValidationError("Each permission must be a string.")

        return value