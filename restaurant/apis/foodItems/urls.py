from rest_framework.routers import DefaultRouter
from .views import FoodItemViewSet

router = DefaultRouter()

router.register(
    r"food-items",
    FoodItemViewSet,
    basename="food-items"
)

urlpatterns = router.urls