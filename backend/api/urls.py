from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('', include('users.urls')),
]
