# serializers.py

from rest_framework import serializers
from ...models import Order, OrderItem


class OrderItemListSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(
        source="food_item.name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "food_item",
            "food_item_name",
            "item_name",
            "item_price",
            "quantity",
            "discount_amount",
            "total_amount",
            "special_instruction",
            "is_active",
            "created_at",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "organization",
            "organization_name",
            "user",
            "user_name",
            "order_type",
            "status",
            "payment_status",
            "customer_name",
            "customer_mobile",
            "table_number",
            "no_of_people",
            "subtotal_amount",
            "discount_amount",
            "tax_amount",
            "delivery_charge",
            "total_amount",
            "payable_amount",
            "items_count",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_items_count(self, obj):
        return obj.items.filter(is_deleted=False).count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemListSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "organization",
            "organization_name",
            "user",
            "user_name",
            "order_number",
            "order_type",
            "status",
            "payment_status",
            "subtotal_amount",
            "discount_amount",
            "tax_amount",
            "delivery_charge",
            "points_used",
            "points_discount_amount",
            "total_amount",
            "payable_amount",
            "coupon_code",
            "customer_name",
            "customer_mobile",
            "table_number",
            "no_of_people",
            "delivery_address",
            "special_instruction",
            "cancel_reason",
            "confirmed_at",
            "completed_at",
            "cancelled_at",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        ]


class CreateOrderItemSerializer(serializers.Serializer):
    food_item = serializers.IntegerField(required=False, allow_null=True)
    item_name = serializers.CharField(required=False, allow_blank=True)
    item_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(default=1)
    discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    special_instruction = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


class CreateOrderSerializer(serializers.Serializer):
    organization = serializers.IntegerField()

    order_type = serializers.ChoiceField(
        choices=Order.ORDER_TYPE_CHOICES,
        default="dine_in"
    )

    payment_status = serializers.ChoiceField(
        choices=Order.PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    customer_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    customer_mobile = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    table_number = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    no_of_people = serializers.IntegerField(required=False, allow_null=True)

    delivery_address = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    special_instruction = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    tax_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    delivery_charge = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    points_used = serializers.IntegerField(default=0)
    points_discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    items = CreateOrderItemSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order items are required")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Order.ORDER_STATUS_CHOICES,
        required=False
    )
    payment_status = serializers.ChoiceField(
        choices=Order.PAYMENT_STATUS_CHOICES,
        required=False
    )
    cancel_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def validate(self, attrs):
        if "status" not in attrs and "payment_status" not in attrs:
            raise serializers.ValidationError(
                "Only status or payment_status can be updated"
            )
        return attrs