from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from applications.posts.models import Post
from .filter import PostFilter
from .permissions import IsOwnerOrReadOnly
from .serializer import PostSerializer
from .toxicity_model import toxicity_model


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ["header", "body"]
    ordering_fields = ["id", "date_posted"]
    ordering = ["-date_posted"]

    def create(self, request, *args, **kwargs):
        check = toxicity_model.text2toxicity(f"{request.data['header']}\n{request.data['body']}",
                                             aggregate=True)
        if check > 0.5:
            return Response({"error": "ToxicityError",
                             "message": "Toxicity check failed"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
