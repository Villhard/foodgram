import django_filters
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = django_filters.BaseInFilter(
        field_name='author',
        lookup_expr='in',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter',
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter',
    )

    def filter(self, queryset, name, value):
        query_params = {
            'is_in_shopping_cart': 'shopping_cart__user',
            'is_favorited': 'favorites__user',
        }
        if value and not self.request.user.is_anonymous:
            return queryset.filter(
                **{query_params[name]: self.request.user}
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')
