import csv
from django.db.models import Sum
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
    AmountIngredient,
)
from users.models import CustomUser, Subscriptions


class CustomUserViewSet(UserViewSet):
    """ViewSet для управления пользовательскими данными."""

    permission_classes = [IsAuthenticatedOrReadOnly,]
    pagination_class = CustomPaginator

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user, context={'request': request})
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
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


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
        return self._toggle_list(request, pk, Favorites)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,])
    def shopping_cart(self, request, pk=None):
        return self._toggle_list(request, pk, Cart)

    def _toggle_list(self, request, pk, model):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer = AddToRecipeSerializer(recipe)
        if request.method == 'POST':
            if model.objects.filter(user=request.user, recipe=recipe).exists():
                return Response({
                    'errors': 'Рецепт уже добавлен в список'
                }, status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not model.objects.filter(user=request.user, recipe=recipe).exists():
                return Response({
                    'errors': 'Такого рецепта нет в списке'
                }, status=status.HTTP_400_BAD_REQUEST)
            model.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    # @action(detail=True, methods=['post', 'delete'],
    #         permission_classes=[IsAuthenticated,])
    # def favorite(self, request, pk=None):
    #     recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
    #     serializer = AddToRecipeSerializer(recipe)
    #     if request.method == 'POST':
    #         if Favorites.objects.filter(user=request.user, recipe=recipe).exists():
    #             return Response({
    #                 'errors': 'Рецепт уже добавлен в избранное'
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #         Favorites.objects.create(user=request.user, recipe=recipe)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     if request.method == 'DELETE':
    #         if not Favorites.objects.filter(user=request.user, recipe=recipe).exists():
    #             return Response({
    #                 'errors': 'Такого рецепта нет в избранном'
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #         Favorites.objects.filter(user=request.user, recipe=recipe).delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(detail=True, methods=['post', 'delete'],
    #         permission_classes=[IsAuthenticated,])
    # def shopping_cart(self, request, pk=None):
    #     recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
    #     serializer = AddToRecipeSerializer(recipe)
    #     if request.method == 'POST':
    #         if Cart.objects.filter(user=request.user, recipe=recipe).exists():
    #             return Response({
    #                 'errors': 'Рецепт уже добавлен в список'
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #         Cart.objects.create(user=request.user, recipe=recipe)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     if request.method == 'DELETE':
    #         if not Cart.objects.filter(user=request.user,
    #                                    recipe=recipe).exists():
    #             return Response({
    #                 'errors': ' Такого рецепта нет в списке'
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #         Cart.objects.filter(user=request.user, recipe=recipe).delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(detail=False, methods=['get'],
    #         permission_classes=[IsAuthenticated,])
    # def download_shopping_cart(self, request):
    #     user = request.user
    #     recipes_in_cart = Cart.objects.filter(user=user)
    #     response = HttpResponse(content_type='text/csv; charset=utf-8')
    #     response['Content-Disposition'] = 'attachment; '
    #     'filename="shopping_cart.csv"'
    #     writer = csv.writer(response)
    #     writer.writerow(['Recipe Name', 'Ingredients', 'Cooking Time'])
    #     for recipe in recipes_in_cart:
    #         ingredients = ', '.join(
    #             [f'{amount_ingredient.amount}'
    #              '{amount_ingredient.ingredients.name}'
    #              for amount_ingredient in recipe.ingredients.all()]
    #         )
    #         writer.writerow([recipe.name, ingredients, recipe.cooking_time])
    #     return response

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            raise AuthenticationFailed()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = AmountIngredient.objects.filter(
            recipe__in_cart__user=request.user
        ).values_list(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        for item in ingredients:
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
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.csv"'
        writer = csv.writer(response)
        writer.writerow(['Наименование ингредиента', 'Единица измерения', 'Количество'])
        for ingredient, info in final_list.items():
            writer.writerow([ingredient, info['measurement_unit'], info['amount']])
        return response
