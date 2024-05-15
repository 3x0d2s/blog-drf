from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register('api/categories', CategoryViewSet)

urlpatterns = router.urls
