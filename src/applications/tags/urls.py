from rest_framework.routers import DefaultRouter
from .views import TagViewSet

router = DefaultRouter()
router.register('api/tags', TagViewSet)

urlpatterns = router.urls
