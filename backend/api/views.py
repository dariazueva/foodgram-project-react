import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filter import RecipeFilter
from api.pagination import CustomPaginator
from api.permissions import AdminOrReadOnly, AuthorAdminOrReadOnly
from api.serializers import (AddToRecipeSerializer, CustomUserSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeGetSerializer, SubscriptionsSerializer,
                             TagSerializer)
from recipes.models import (AmountIngredient, Cart, Favorites, Ingredient,
                            Recipe, Tag)
from users.models import CustomUser, Subscriptions


class CustomUserViewSet(UserViewSet):
    """ViewSet для управления пользовательскими данными."""

    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = CustomPaginator

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user,
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(CustomUser, pk=self.kwargs['id'])
        if user == author:
            return Response({'Нельзя подписаться на самого себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscriptions.objects.get_or_create(
            user=user, author=author
        )
        if created:
            serializer = SubscriptionsSerializer(
                subscription,
                context={'request': request},
                is_subscribed=True
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'Вы уже подписаны на данного пользователя.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(CustomUser, pk=self.kwargs['id'])
        subscription = Subscriptions.objects.filter(user=user,
                                                    author=author).first()
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'Вы не подписаны на данного пользователя.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = Subscriptions.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AdminOrReadOnly, ]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для управления ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = [AuthorAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk=None):
        return self.add_to_list(request, pk, Favorites)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk=None):
        return self.add_to_list(request, pk, Cart)

    @favorite.mapping.delete
    def remove_from_favorites(self, request, pk=None):
        return self.remove_from_list(request, pk, Favorites)

    @shopping_cart.mapping.delete
    def remove_from_cart(self, request, pk=None):
        return self.remove_from_list(request, pk, Cart)

    def add_to_list(self, request, pk, model):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response({'Такого рецепта не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = AddToRecipeSerializer(recipe)
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            return Response({'Рецепт уже добавлен в список.'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_list(self, request, pk, model):
        recipe = get_object_or_404(Recipe, id=pk)
        if not model.objects.filter(user=request.user,
                                    recipe=recipe).exists():
            return Response({'Такого рецепта нет в списке.'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            raise AuthenticationFailed()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredient = AmountIngredient.objects.filter(
            recipe__cart_recipe__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        for item in ingredient:
            if len(item) == 2:
                name, measurement_unit = item
                amount = 0
            elif len(item) == 3:
                name, measurement_unit, amount = item
            else:
                continue
            final_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; '
        'filename="shopping_cart.csv"'
        writer = csv.writer(response)
        writer.writerow(['Наименование ингредиента', 'Единица измерения',
                         'Количество'])
        for ingredient, info in final_list.items():
            writer.writerow([ingredient, info['measurement_unit'],
                             info['amount']])
        return response
