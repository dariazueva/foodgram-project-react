from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель 'Ингредиент'."""

    name = models.CharField('Ингредиент', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель 'Тег'."""

    name = models.CharField('Тег', max_length=200, unique=True)
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=[RegexValidator(regex='^#([a-fA-F0-9]{6})',)])
    slug = models.SlugField('Слаг', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель 'Рецепт'."""

    name = models.CharField('Название', max_length=200,
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
        through='recipes.AmountIngredient'
    )
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  related_name='recipes',
                                  blank=False,
                                  )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        default=0,
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
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveBigIntegerField(
        verbose_name='Количество',
        default=0,
        validators=[MinValueValidator(limit_value=1)]
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.amount} {self.ingredients}'


class Favorites(models.Model):
    """Модель 'Избранное'."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorite_user',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Cart(models.Model):
    """Модель 'Корзина'."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        related_name='in_cart',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Автор списка',
        related_name='cart',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.recipe.name}'
