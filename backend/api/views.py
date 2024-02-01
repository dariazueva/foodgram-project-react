import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.response import Response

from api.serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer
)
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorites,
    Cart,
)


class CustomUserViewSet(UserViewSet):
    """ViewSet для управления пользовательскими данными."""

    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        user = request.user
        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            Favorites.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Favorites.objects.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def get_is_in_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        user = request.user
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            Cart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Cart.objects.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        recipes_in_cart = Recipe.objects.filter(cart__user=user)
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; '
        'filename="shopping_cart.csv"'
        writer = csv.writer(response)
        writer.writerow(['Recipe Name', 'Ingredients', 'Cooking Time'])
        for recipe in recipes_in_cart:
            ingredients = ', '.join(
                [f'{amount_ingredient.amount}'
                 '{amount_ingredient.ingredients.name}'
                 for amount_ingredient in recipe.ingredients.all()]
            )
            writer.writerow([recipe.name, ingredients, recipe.cooking_time])
        return response
