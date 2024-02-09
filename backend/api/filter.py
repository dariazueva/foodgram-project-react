from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Настройка фильтра для рецептов."""

    tags = filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('tags',)
