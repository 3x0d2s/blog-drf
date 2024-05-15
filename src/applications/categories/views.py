from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from .models import Category


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
