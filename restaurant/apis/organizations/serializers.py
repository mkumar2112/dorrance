from rest_framework import serializers
from ...models import Organization, OrgAdmin


class OrganizationSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "uuid",
            "name",
            "slug",
            "logo",
            "logo_url",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "latitude",
            "longitude",
            "opening_time",
            "closing_time",
            "description",
            "is_active",
            "is_verified",
            "is_deleted",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "uuid",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        request = self.context.get("request")

        if obj.logo:
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url

        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
    


class OrgAdminSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = OrgAdmin
        fields = [
            "id",
            "user",
            "user_name",
            "organization",
            "organization_name",
            "is_primary",
            "can_manage_users",
            "can_manage_menu",
            "can_manage_orders",
            "can_view_reports",
            "can_manage_payments",
            "is_active",
            "is_deleted",
            "joined_at",
        ]
        read_only_fields = ["id", "joined_at"]

    def validate(self, attrs):
        user = attrs.get("user") or getattr(self.instance, "user", None)
        organization = attrs.get("organization") or getattr(self.instance, "organization", None)

        qs = OrgAdmin.objects.filter(
            user=user,
            organization=organization,
            is_deleted=False,
        )

        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                "This user is already admin of this organization."
            )

        return attrs












