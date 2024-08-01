from io import StringIO
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets, mixins
from django.db import models
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
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from favorites.models import Favorite
from shopping.models import ShoppingCart
from api.permissions import IsAuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
from backend.settings import HOST


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


class RecipeViewSet(viewsets.ModelViewSet):
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

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            user = request.user
            recipe = self.get_object()
            try:
                ShoppingCart.objects.create(user=user, recipe=recipe)
                serializer = ShortRecipeSerializer(recipe)
                return Response(serializer.data, status=201)
            except IntegrityError:
                return Response(
                    {'detail': 'Рецепт уже добавлен в список покупок'},
                    status=400,
                )
        elif request.method == 'DELETE':
            user = request.user
            recipe = self.get_object()
            try:
                favorite = ShoppingCart.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=204)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {'detail': 'Рецепт не найден в списке покупок'},
                    status=400,
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
                f'{ingredient["ingredient__name"]} - {ingredient["total_amount"]} '
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
            {'short-link': f'{HOST}/recipes/{pk}'}, status=status.HTTP_200_OK
        )
