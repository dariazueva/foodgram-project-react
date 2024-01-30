from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Cart,
    Favorites,
    AmountIngredient
)


admin.site.empty_value_display = 'Не задано'


class RecipeResource(resources.ModelResource):
    """Ресурс для экспорта и импорта рецепта."""

    class Meta:
        model = Recipe


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    """Администратор для модели Recipe."""

    resource_classes = [RecipeResource]
    list_display = (
        'name',
        'author',
        'cooking_time',
        'text',
        'image',
        'count_favorites',
        )
    list_filter = ('name', 'author__username', 'tags__name',)
    list_editable = (
        'cooking_time',
        'text',
        'image',
        'author',
    )
    list_display_links = ('name',)

    def count_favorites(self, obj: Recipe):
        return obj.favorite_recipe.count()


class TagResource(resources.ModelResource):
    """Ресурс для экспорта и импорта тегов."""

    class Meta:
        model = Tag


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    """Администратор для модели Tag."""

    resource_classes = [TagResource]
    list_display = ('name', 'color', 'slug')
    list_editable = ('color', 'slug',)


class IngredientResource(resources.ModelResource):
    """Ресурс для экспорта и импорта ингредиентов."""

    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Администратор для модели Ingredient."""

    resource_classes = [IngredientResource]
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class FavoritesResource(resources.ModelResource):
    """Ресурс для экспорта и импорта избранного."""

    class Meta:
        model = Favorites


@admin.register(Favorites)
class FavoritesAdmin(ImportExportModelAdmin):
    """Администратор для модели Favorites."""

    resource_classes = [FavoritesResource]
    list_display = ('user', 'recipe',)


class AmountIngredientResource(resources.ModelResource):
    """Ресурс для экспорта и импорта ингредиентов в рецепте."""

    class Meta:
        model = AmountIngredient


@admin.register(AmountIngredient)
class AmountIngredientAdmin(ImportExportModelAdmin):
    """Администратор для модели AmountIngredient."""

    resource_classes = [AmountIngredientResource]
    list_display = ('recipe', 'ingredient', 'amount',)
    list_editable = ('amount',)


class CartResource(resources.ModelResource):
    """Ресурс для экспорта и импорта корзины."""

    class Meta:
        model = Cart


@admin.register(Cart)
class CartAdmin(ImportExportModelAdmin):
    """Администратор для модели Cart."""

    resource_classes = [CartResource]
    list_display = ('user', 'recipe',)
