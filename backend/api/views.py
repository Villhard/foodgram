from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe
from favorites.models import Favorite
from api.permissions import IsAuthorOrReadOnly


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            user = request.user
            recipe = self.get_object()
            try:
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = ShortRecipeSerializer(recipe)
                return Response(serializer.data, status=201)
            except IntegrityError:
                return Response(
                    {'detail': 'Рецепт уже добавлен в избранное'},
                    status=400,
                )
        elif request.method == 'DELETE':
            user = request.user
            recipe = self.get_object()
            try:
                favorite = Favorite.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=204)
            except Favorite.DoesNotExist:
                return Response(
                    {'detail': 'Рецепт не найден в избранном'},
                    status=400,
                )
