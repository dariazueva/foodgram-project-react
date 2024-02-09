from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Модель 'Пользователь'."""

    username = models.CharField(
        'Уникальный юзернейм',
        max_length=150,
        unique=True
    )
    email = models.EmailField('Адрес электронной почты', max_length=254)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель 'Подписки'."""

    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
