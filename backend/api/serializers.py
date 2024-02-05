from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    AmountIngredient,
    Favorites,
    Cart
)
from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользовательской модели."""

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


# class CustomUserCreateSerializer(UserCreateSerializer):
#     """Сериализатор для создания пользователя."""

#     email = serializers.EmailField()
#     username = serializers.CharField()

#     class Meta:
#         model = CustomUser
#         fields = ('email', 'id', 'username', 'first_name', 'last_name')
#         extra_kwargs = {
#             'email': {'required': True},
#             'username': {'required': True},
#             'password': {'required': True},
#             'first_name': {'required': True},
#             'last_name': {'required': True},
#         }


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


class AddToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в список покупок и в избранное рецептов."""

    image = Base64ImageField

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        return Favorites.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        return Cart.objects.filter(user=user, recipe=obj).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        image_data = validated_data.pop('image', [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        for tag_data in tags_data:
            Tag.objects.create(recipe=recipe, **tag_data)
        if image_data:
            recipe.image.save(image_data.name, image_data, save=True)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        image_data = validated_data.get('image', instance.image)
        ingredients_data = validated_data.get('ingredients', [])
        instance.ingredients.all().delete()
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=instance, **ingredient_data)
        tags_data = validated_data.get('tags', [])
        instance.tags.all().delete()
        for tag_data in tags_data:
            Tag.objects.create(recipe=instance, **tag_data)
        if image_data:
            instance.image.save(image_data.name, image_data, save=True)
        elif 'image' in validated_data:
            instance.image.delete()
        instance.save()
        return instance

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
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
