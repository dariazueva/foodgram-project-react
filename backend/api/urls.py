from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (TagViewSet, RecipeViewSet, IngredientViewSet,
                       CustomUserViewSet)


router_version1 = DefaultRouter()

router_version1.register(
    'tags',
    TagViewSet)
router_version1.register(
    'recipes',
    RecipeViewSet)
router_version1.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router_version1.register(
    'users',
    CustomUserViewSet,
    basename='users'
)
router_version1.register(
    r'recipes/(?P<recipes_id>\d+)/favorite',
    RecipeViewSet,
    basename='favorite'
)
router_version1.register(
    r'users/(?P<users_id>\d+)/subscribe',
    CustomUserViewSet,
    basename='subscribe'
)


urlpatterns = [
    path('', include(router_version1.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
