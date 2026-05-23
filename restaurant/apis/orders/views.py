# views.py

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from ...models import Order, OrderItem, FoodItem
from .serializers import (
    CreateOrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    UpdateOrderStatusSerializer,
)


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data
            user = request.user
            items = data.pop("items")

            order = Order.objects.create(
                organization_id=data.get("organization"),
                user=user,
                created_by=user,

                order_type=data.get("order_type", "dine_in"),
                status="pending",
                payment_status=data.get("payment_status", "pending"),

                customer_name=data.get("customer_name"),
                customer_mobile=data.get("customer_mobile"),

                table_number=data.get("table_number"),
                no_of_people=data.get("no_of_people"),
                delivery_address=data.get("delivery_address"),

                coupon_code=data.get("coupon_code"),
                special_instruction=data.get("special_instruction"),

                discount_amount=data.get("discount_amount", 0),
                tax_amount=data.get("tax_amount", 0),
                delivery_charge=data.get("delivery_charge", 0),

                points_used=data.get("points_used", 0),
                points_discount_amount=data.get("points_discount_amount", 0),
            )

            subtotal = Decimal("0.00")

            for item in items:
                food_item = None

                food_item_id = item.get("food_item")
                if food_item_id:
                    food_item = FoodItem.objects.filter(id=food_item_id).first()

                item_price = item.get("item_price", Decimal("0.00"))
                quantity = item.get("quantity", 1)
                discount_amount = item.get("discount_amount", Decimal("0.00"))

                total_amount = (item_price * quantity) - discount_amount
                subtotal += total_amount

                OrderItem.objects.create(
                    order=order,
                    food_item=food_item,
                    item_name=item.get(
                        "item_name"
                    ) or food_item.name if food_item else item.get("item_name", ""),
                    item_price=item_price,
                    quantity=quantity,
                    discount_amount=discount_amount,
                    total_amount=total_amount,
                    special_instruction=item.get("special_instruction"),
                )

            order.subtotal_amount = subtotal
            order.calculate_total()
            order.save()

            return Response({
                "success": True,
                "message": "Order created successfully",
                "data": OrderDetailSerializer(order).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Order.objects.filter(
            is_deleted=False
        ).select_related(
            "organization",
            "user"
        ).prefetch_related(
            "items"
        ).order_by("-id")

        organization_id = request.GET.get("organization")
        order_type = request.GET.get("order_type")
        order_status = request.GET.get("status")
        payment_status = request.GET.get("payment_status")
        customer_mobile = request.GET.get("customer_mobile")
        search = request.GET.get("search")
        is_active = request.GET.get("is_active")

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        if order_type:
            queryset = queryset.filter(order_type=order_type)

        if order_status:
            queryset = queryset.filter(status=order_status)

        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        if customer_mobile:
            queryset = queryset.filter(customer_mobile__icontains=customer_mobile)

        if search:
            queryset = queryset.filter(
                order_number__icontains=search
            ) | queryset.filter(
                customer_name__icontains=search
            ) | queryset.filter(
                customer_mobile__icontains=search
            ) | queryset.filter(
                table_number__icontains=search
            )

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        paginator = OrderPagination()
        paginated_orders = paginator.paginate_queryset(queryset, request)

        serializer = OrderListSerializer(paginated_orders, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Orders fetched successfully",
            "data": serializer.data
        })


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = Order.objects.filter(
            id=order_id,
            is_deleted=False
        ).select_related(
            "organization",
            "user"
        ).prefetch_related(
            "items"
        ).first()

        if not order:
            return Response({
                "success": False,
                "message": "Order not found"
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "message": "Order fetched successfully",
            "data": OrderDetailSerializer(order).data
        }, status=status.HTTP_200_OK)


class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = Order.objects.filter(
            id=order_id,
            is_deleted=False
        ).first()

        if not order:
            return Response({
                "success": False,
                "message": "Order not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateOrderStatusSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        new_status = data.get("status")
        new_payment_status = data.get("payment_status")

        if new_status:
            order.status = new_status

            if new_status == "confirmed" and not order.confirmed_at:
                order.confirmed_at = timezone.now()

            elif new_status == "completed" and not order.completed_at:
                order.completed_at = timezone.now()

            elif new_status == "cancelled":
                order.cancelled_at = timezone.now()
                order.cancel_reason = data.get("cancel_reason")

        if new_payment_status:
            order.payment_status = new_payment_status

        order.save()

        return Response({
            "success": True,
            "message": "Order updated successfully",
            "data": OrderDetailSerializer(order).data
        }, status=status.HTTP_200_OK)


class DeleteOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, order_id):
        order = Order.objects.filter(
            id=order_id,
            is_deleted=False
        ).first()

        if not order:
            return Response({
                "success": False,
                "message": "Order not found"
            }, status=status.HTTP_404_NOT_FOUND)

        order.is_deleted = True
        order.is_active = False
        order.save()

        return Response({
            "success": True,
            "message": "Order deleted successfully"
        }, status=status.HTTP_200_OK)