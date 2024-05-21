from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register('api/posts', PostViewSet)

urlpatterns = router.urls
