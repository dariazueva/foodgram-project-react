import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe, Tag, Ingredient, AmountIngredient
from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользовательской модели."""

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AmountIngredient."""

    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    # ingredients = AmountIngredientSerializer(read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                #   'is_favorited',
                #   'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                )

    

    # def to_internal_value(self, data):
    #     image_data = base64.b64decode(data.get('image', ''))
    #     temp_image = ContentFile(image_data, name='temp_image.png')
    #     data['image'] = temp_image
    #     return super().to_internal_value(data)
