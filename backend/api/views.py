from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """ViewSet для управления пользовательскими данными."""

    permission_classes = (IsAuthenticatedOrReadOnly,)
