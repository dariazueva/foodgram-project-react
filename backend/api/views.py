import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.response import Response

from api.filter import RecipeFilter
from api.pagination import CustomPaginator
from api.permissions import AdminOrReadOnly, AuthorAdminOrReadOnly
from api.serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    AddToRecipeSerializer,
    SubscribeSerializer,
    CustomUserSerializer,
)
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorites,
    Cart,
)
from users.models import CustomUser, Subscriptions


class CustomUserViewSet(UserViewSet):
    """ViewSet для управления пользовательскими данными."""

    permission_classes = [IsAuthenticatedOrReadOnly,]
    pagination_class = CustomPaginator
    # serializer_class = SubscribeSerializer
    # serializer_class = CustomUserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,])
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(CustomUser, pk=self.kwargs['id'])
        if user == author:
            return Response({'errors': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            subscription, created = Subscriptions.objects.get_or_create(user=user, author=author)
            if created:
                serializer = SubscribeSerializer(subscription,
                                             context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': 'Вы уже подписаны на данного пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            subscription = Subscriptions.objects.filter(user=user, author=author).first()
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': 'Вы не подписаны на данного пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = Subscriptions.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AdminOrReadOnly,]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AuthorAdminOrReadOnly,]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        user = request.user
        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            Favorites.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Favorites.objects.create(user=user, recipe=recipe)
            serializer = AddToRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        user = request.user
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            Cart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Cart.objects.create(user=user, recipe=recipe)
            serializer = AddToRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated,])
    def download_shopping_cart(self, request):
        user = request.user
        recipes_in_cart = Cart.objects.filter(user=user)
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

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            raise AuthenticationFailed()
