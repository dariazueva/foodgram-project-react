from djoser.serializers import UserSerializer

from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользовательской модели."""

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
