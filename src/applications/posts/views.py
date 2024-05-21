from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from applications.posts.models import Post
from applications.common.permissions import IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .serializer import PostSerializer
from .filter import PostFilter


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ["header", "body"]
    ordering_fields = ["id", "date_posted"]
    ordering = ["-date_posted"]
