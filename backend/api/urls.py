from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'users', UserViewSet)


app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('users/', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
