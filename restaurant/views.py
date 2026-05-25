from django.shortcuts import render
from .models import *
# Create your views here.


class OrganizationView:
    def organization_list(request):
        return render(request, "restaurant/organizations/layout.html")
    
    def organization_gallery_list(request):
        return render(request, "restaurant/organizations/gallery.html")




class FoodCategoryView:
    def food_category_list(request):
        return render(request, "restaurant/foodCategories/layout.html")    


class FoodItemsView:
    def food_items_list(request):
        return render(request, "restaurant/foodItems/layout.html")    




class DineInView:
    def dine_in_list(request):
        return render(request, "restaurant/dineIn/layout.html")  
      
    def dine_in_booking_list(request):
        return render(request, "restaurant/dineInBooking/layout.html")    














