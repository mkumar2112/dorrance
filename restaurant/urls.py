from django.urls import path
from .views import *

urlpatterns = [
    path("organizations/", OrganizationView.organization_list, name="organization_list"),
    path("food-categories/", FoodCategoryView.food_category_list, name="food_category_list"),
    path("food-items/", FoodItemsView.food_items_list, name="food_items_list"),
    path("dine-in/", DineInView.dine_in_list, name="dine_in_list"),
    path("dine-in-bookings/", DineInView.dine_in_booking_list, name="dine_in_booking_list"),
]
