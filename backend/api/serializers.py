import re
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    AmountIngredient,
    Favorites,
    Cart
)
from users.models import CustomUser, Subscriptions


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользовательской модели."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True,
                         'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return Subscriptions.objects.filter(user=user, author=obj).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context['request'].method == 'POST':
            data.pop('is_subscribed', None)
        return data

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже зарегистрирован')
        return value

    def validate_username(self, value):
        pattern = r'^[\w.@+-]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Некорректное имя пользователя')
        return value


class AddToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в список покупок и в избранное рецептов."""

    image = Base64ImageField

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для модели Subscriptions."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and isinstance(obj, CustomUser):
            return Subscriptions.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.user.recipes.count()

    def get_recipes(self, obj):
        if isinstance(obj, CustomUser):
            recipes = Recipe.objects.filter(author=obj)
            return RecipeSerializer(recipes, many=True, read_only=True).data


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

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    # ingredients = AmountIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        return self._check_item_in_list(obj, Favorites)

    def get_is_in_shopping_cart(self, obj):
        return self._check_item_in_list(obj, Cart)

    def _check_item_in_list(self, obj, model):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return model.objects.filter(user=user, recipe=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ingredients'] = AmountIngredientSerializer(instance.ingredients.all(), many=True).data
        return representation


    # def get_is_favorited(self, obj):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         user = request.user
    #         return Favorites.objects.filter(user=user, recipe=obj).exists()
    #     return False

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         user = request.user
    #         return Cart.objects.filter(user=user, recipe=obj).exists()
    #     return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        image_data = validated_data.pop('image', [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data).save()
        for tag_data in tags_data:
            Tag.objects.create(recipe=recipe, **tag_data).save()
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
