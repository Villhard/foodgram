from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    list_display = ('name', 'author', 'favorite_count')

    @staticmethod
    def favorite_count(obj):
        return obj.favorites.count()

    favorite_count.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Tag)
