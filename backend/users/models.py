from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (USER_USERNAME_MAX,
                             USER_EMAIL_MAX,
                             FIRST_NAME_MAX,
                             LAST_NAME_MAX)

class CustomUser(AbstractUser):
    """Модель 'Пользователь'."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        'Уникальный юзернейм',
        max_length=USER_USERNAME_MAX,
        unique=True
    )
    email = models.EmailField('Email', max_length=USER_EMAIL_MAX,
                               unique=True)
    first_name = models.CharField('First name', max_length=150, blank=True)
    last_name = models.CharField('Last name', max_length=LAST_NAME_MAX,
                                 blank=True)

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
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_for_author',
            ),
    )

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
