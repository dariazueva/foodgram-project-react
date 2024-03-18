from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from recipes.constants import (INGREDIENT_NAME_MAX,
                              MEASUREMENT_UNIT_MAX,
                              TAG_NAME_MAX,
                              COLOR_NAME_MAX,
                              TAG_SLUG_MAX,
                              RECIPE_NAME_MAX,
                              COOKING_TIME_DEFAULT,
                              AMOUNT_DEFAULT)

User = get_user_model()


class Ingredient(models.Model):
    """Модель 'Ингредиент'."""

    name = models.CharField('Ingredient', max_length=INGREDIENT_NAME_MAX)
    measurement_unit = models.CharField('Measurement_unit', max_length=MEASUREMENT_UNIT_MAX)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient',
            ),
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель 'Тег'."""

    name = models.CharField('Tag', max_length=TAG_NAME_MAX, unique=True)
    color = ColorField(
        'Цвет',
        max_length=COLOR_NAME_MAX,
        unique=True,
        validators=[RegexValidator(regex='^#([a-fA-F0-9]{6})',)])
    slug = models.SlugField('Slug', max_length=TAG_SLUG_MAX, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель 'Рецепт'."""

    name = models.CharField('Recipe', max_length=RECIPE_NAME_MAX,
                            blank=False, null=False)
    image = models.ImageField('Картинка',
                              upload_to='recipes/images/',
                              default=None,
                              blank=False, null=False
                              )
    text = models.TextField('Описание', blank=False, null=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        blank=False,
        through='AmountIngredient'
    )
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  related_name='recipes',
                                  blank=False,
                                  )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        default=COOKING_TIME_DEFAULT,
        validators=(
            MinValueValidator(limit_value=1),
        ),
        blank=False, null=False
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
        blank=False, null=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    """Модель 'Ингредиенты в рецепте'."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient',
        on_delete=models.CASCADE,
        db_column='ingredients_id'
    )
    amount = models.PositiveBigIntegerField(
        verbose_name='Количество',
        default=AMOUNT_DEFAULT,
        validators=[MinValueValidator(limit_value=1)]
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_for_recipe',
            ),
        )


    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class BaseListModel(models.Model):
    """Abstract model for cart and favorites models."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe',
    )
    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='%(class)s_user',
    )
    pub_date = models.DateTimeField(
       'Publication date',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Favorites(BaseListModel):
    """Модель 'Избранное'."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Cart(BaseListModel):
    """Модель 'Корзина'."""

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.recipe.name}'
