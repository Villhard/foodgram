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

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
