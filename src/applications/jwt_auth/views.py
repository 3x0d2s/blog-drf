from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .models import User
from .serializers import UserSerializer
from .permissions import IsNotAuthenticated, IsAccountOwnerOrAdmin


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsNotAuthenticated]
        else:
            permission_classes = [IsAccountOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    @action(url_path='me', detail=False, methods=['get'])
    def get_me(self, request):
        serializer = self.get_serializer(request.user)
        return Response({'data': serializer.data})
