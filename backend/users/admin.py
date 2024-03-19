from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from users.models import CustomUser, Subscriptions


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    """Администратор для модели CustomUser."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_subscriptions_count',
        'get_recipes_count',
    )
    list_editable = (
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('first_name', 'email')
    list_display_links = ('username',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            subscriptions_count=Count('subscriptions'),
            recipes_count=Count('recipes', distinct=True)
        )
        return queryset

    def get_subscriptions_count(self, obj):
        return obj.subscriptions_count
    get_subscriptions_count.short_description = 'Subscriptions count'

    def get_recipes_count(self, obj):
        return obj.recipes_count
    get_recipes_count.short_description = 'Recipes count'


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Администратор для модели Subscriptions."""

    list_display = ('user', 'author',)
    list_editable = ('author',)
    list_display_links = ('user',)
