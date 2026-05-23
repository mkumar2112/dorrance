# urls.py

from django.urls import path
from .views import (
    CreateOrderAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
    UpdateOrderStatusAPIView,
    DeleteOrderAPIView,
)

urlpatterns = [
    path(
        "orders/",
        OrderListAPIView.as_view(),
        name="order-list"
    ),

    path(
        "orders/create/",
        CreateOrderAPIView.as_view(),
        name="create-order"
    ),

    path(
        "orders/<int:order_id>/",
        OrderDetailAPIView.as_view(),
        name="order-detail"
    ),

    path(
        "orders/<int:order_id>/update-status/",
        UpdateOrderStatusAPIView.as_view(),
        name="update-order-status"
    ),

    path(
        "orders/<int:order_id>/delete/",
        DeleteOrderAPIView.as_view(),
        name="delete-order"
    ),
]