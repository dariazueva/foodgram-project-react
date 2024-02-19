from django.contrib import admin

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Cart,
    Favorites,
    AmountIngredient
)


admin.site.empty_value_display = 'Не задано'


class IngredientInline(admin.TabularInline):
    model = AmountIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администратор для модели Recipe."""

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
    inlines = (IngredientInline,)

    def count_favorites(self, obj: Recipe):
        return obj.favorite_recipe.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администратор для модели Tag."""

    list_display = ('name', 'color', 'slug')
    list_editable = ('color', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администратор для модели Ingredient."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Администратор для модели Favorites."""

    list_display = ('user', 'recipe',)


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    """Администратор для модели AmountIngredient."""

    list_display = ('recipe', 'ingredient', 'amount',)
    list_editable = ('amount',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Администратор для модели Cart."""

    list_display = ('user', 'recipe',)
