from rest_framework.viewsets import ModelViewSet
from applications.posts.models import Post
from applications.common.permissions import IsAdminOrReadOnly
from .serializer import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrReadOnly]
