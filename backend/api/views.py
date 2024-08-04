from io import StringIO

from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import BaseRecipeAction
from api.paginations import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, ExtendedCustomUserSerializer,
                             IngredientSerializer, RecipeSerializer,
                             TagSerializer)
from api.utils import Base52
from backend.settings import HOST
from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from shopping.models import ShoppingCart
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserViewSet):
    pagination_class = CustomPagination

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('put', 'delete'),
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            if serializer.is_valid():
                user.avatar = serializer.validated_data['avatar']
                user.save()
                return Response(
                    {'avatar': user.avatar.url}, status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=ExtendedCustomUserSerializer,
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user

        subscriptions = Subscription.objects.filter(follower=user).values_list(
            'following', flat=True
        )
        following_users = User.objects.filter(id__in=subscriptions)

        paginator = self.paginator
        result_page = paginator.paginate_queryset(following_users, request)

        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=ExtendedCustomUserSerializer,
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        user = request.user
        author = self.get_object()
        subcription = Subscription.objects.filter(
            follower=user, following=author
        ).first()

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if subcription:
                return Response(
                    {'detail': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscription.objects.create(follower=user, following=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=201)

        if subcription:
            subcription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Вы не подписаны на этого автора'},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
    pagination_class = CustomPagination
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
            request,
            Favorite,
            pk,
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
            request,
            ShoppingCart,
            pk,
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
        short_pk = Base52.to_base52(pk)
        return Response(
            {'short-link': f'{HOST}/rec/{short_pk}'},
            status=status.HTTP_200_OK
        )
