from rest_framework import serializers
from ...models import FoodCategory


class FoodCategorySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FoodCategory
        fields = [
            "id",
            "organization",
            "organization_name",
            "name",
            "slug",
            "image",
            "image_url",
            "description",
            "is_active",
            "is_deleted",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "organization_name",
            "slug",
            "image_url",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url

        return None