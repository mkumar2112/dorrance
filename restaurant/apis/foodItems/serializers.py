from rest_framework import serializers
from ...models import FoodItem, FoodCategory


class FoodItemSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    image_url = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = [
            "id",
            "organization",
            "organization_name",
            "category",
            "category_name",
            "name",
            "slug",
            "image",
            "image_url",
            "description",
            "price",
            "discounted_price",
            "final_price",
            "is_veg",
            "is_spicy",
            "preparation_time",
            "is_available",
            "is_featured",
            "stock_quantity",
            "is_unlimited_stock",
            "rating",
            "total_reviews",
            "sort_order",
            "is_active",
            "is_deleted",
            "created_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "organization",
            "organization_name",
            "slug",
            "image_url",
            "final_price",
            "rating",
            "total_reviews",
            "created_by",
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

    def get_final_price(self, obj):
        return obj.get_final_price()

    def validate_category(self, category):
        request = self.context.get("request")
        organization_id = request.session.get("selected_org") if request else None
        print("Validating category:", category, "for organization_id:", organization_id , category.organization_id)
        if category and organization_id:
            if str(category.organization_id) != organization_id:
                raise serializers.ValidationError(
                    "Selected category does not belong to selected organization."
                )

        return category

    def validate(self, attrs):
        price = attrs.get("price") or getattr(self.instance, "price", None)
        discounted_price = attrs.get("discounted_price")

        if discounted_price is None and self.instance:
            discounted_price = self.instance.discounted_price

        if discounted_price and price and discounted_price > price:
            raise serializers.ValidationError(
                {
                    "discounted_price": "Discounted price cannot be greater than price."
                }
            )

        return attrs