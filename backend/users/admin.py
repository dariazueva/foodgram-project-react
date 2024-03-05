from django.contrib import admin

from users.models import CustomUser, Subscriptions


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Администратор для модели CustomUser."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_editable = (
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('first_name', 'email')
    list_display_links = ('username',)


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Администратор для модели Subscriptions."""

    list_display = ('user', 'author',)
    list_editable = ('author',)
    list_display_links = ('user',)
