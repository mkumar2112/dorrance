from django.shortcuts import render
from .models import *
# Create your views here.


class OrganizationView:
    def organization_list(request):
        return render(request, "restaurant/organizations/layout.html")



class FoodCategoryView:
    def food_category_list(request):
        return render(request, "restaurant/foodCategories/layout.html")    


class FoodItemsView:
    def food_items_list(request):
        return render(request, "restaurant/foodItems/layout.html")    














