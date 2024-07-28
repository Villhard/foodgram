from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.BaseInFilter(
        field_name='author',
        lookup_expr='in',
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
