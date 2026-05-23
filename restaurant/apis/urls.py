from django.urls import path, include

urlpatterns = [
    path("", include("restaurant.apis.organizations.urls")),
    path("", include("restaurant.apis.foodCategories.urls")),
    path("", include("restaurant.apis.foodItems.urls")),
    path("", include("restaurant.apis.dineIn.urls")),
    path("", include("restaurant.apis.orders.urls")),
]