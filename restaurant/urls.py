from django.urls import path
from .views import *

urlpatterns = [
    path("organizations/", OrganizationView.organization_list, name="organization_list"),
    path("food-categories/", FoodCategoryView.food_category_list, name="food_category_list"),
    path("food-items/", FoodItemsView.food_items_list, name="food_items_list"),
]
