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


urlpatterns = [
    path('', include(router_version1.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path('recipes/download_shopping_cart/', RecipeViewSet,
         name='download_shopping_cart')
]
