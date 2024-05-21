from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from .models import Author
from .serializers import AuthorSerializer


class AuthorViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Author.objects.all().filter(user__is_superuser=False)
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
