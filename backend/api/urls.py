from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet)


app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('users/', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
