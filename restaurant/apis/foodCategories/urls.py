from rest_framework.routers import DefaultRouter
from .views import FoodCategoryViewSet

router = DefaultRouter()
router.register(
    r"food-categories",
    FoodCategoryViewSet,
    basename="food-categories"
)

urlpatterns = router.urls
