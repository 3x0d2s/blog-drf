from rest_framework.viewsets import ModelViewSet

from .models import Comment
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import CommentSerializer


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
