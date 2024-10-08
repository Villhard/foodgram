from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter',
    )
    is_favorited = filters.BooleanFilter(
        method='filter',
    )

    def filter(self, queryset, name, value):
        query_params = {
            'is_in_shopping_cart': 'shopping_cart__user',
            'is_favorited': 'favorites__user',
        }
        if value and not self.request.user.is_anonymous:
            return queryset.filter(**{query_params[name]: self.request.user})
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags',)


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
