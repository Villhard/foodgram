from io import StringIO
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from favorites.models import Favorite
from shopping.models import ShoppingCart
from api.permissions import IsAuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
from backend.settings import HOST
from api.mixins import BaseRecipeAction


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
    filterset_class = IngredientFilter


class RecipeViewSet(BaseRecipeAction, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.handle_action(
            request, Favorite, pk,
            'Рецепт уже добавлен в избранное',
            'Рецепт не найден в избранном',
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.handle_action(
            request, ShoppingCart, pk,
            'Рецепт уже добавлен в список покупок',
            'Рецепт не найден в списке покупок',
        )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total_amount=models.Sum('amount'))
        )
        output = StringIO()
        output.write('Список покупок:\n')
        for ingredient in ingredients:
            output.write(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        response = Response(output.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link',
    )
    def get_link(self, request, pk):
        get_object_or_404(Recipe, id=pk)
        return Response(
            {'short-link': f'{HOST}/recipes/{pk}'},
            status=status.HTTP_200_OK
        )
