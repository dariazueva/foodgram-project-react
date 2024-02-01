from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (TagViewSet, RecipeViewSet, IngredientViewSet)

# from api.views import (TagsViewSet, CustomUserViewSet, IngredientsViewSet,
#                        RecipesViewSet, FavoritesViewSet, CartViewSet,
#                        SubscriptionsViewSet, SubscribeViewSet,
#                        TokenObtainView, UserRegistrationViewSet)

router_version1 = DefaultRouter()
# router_version1.register(
#     'users',
#     CustomUserViewSet,
#     basename='user')
router_version1.register(
    r'tags',
    TagViewSet)
router_version1.register(
    r'recipes',
    RecipeViewSet)
router_version1.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
# router_version1.register(
#     r'recipes/(?P<recipes_id>\d+)/favorite',
#     FavoritesViewSet,
#     basename='favorite'
# )
# router_version1.register(
#     r'recipes/(?P<recipes_id>\d+)/shopping_cart',
#     CartViewSet,
#     basename='shopping_cart'
# )
# router_version1.register(
#     r'users/subscriptions',
#     SubscriptionsViewSet,
#     basename='subscriptions'
# )
# router_version1.register(
#     r'users/(?P<users_id>\d+)/subscribe',
#     SubscribeViewSet,
#     basename='subscribe'
# )


urlpatterns = [
    path('', include(router_version1.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
