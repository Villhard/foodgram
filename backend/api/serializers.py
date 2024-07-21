from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Tag, Ingredient, RecipeIngredient, Recipe
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)
    ingredients_detail = RecipeIngredientReadSerializer(
        source='recipeingredient_set', many=True, read_only=True
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    # FIXME: Implement
    def get_is_favorited(self, obj):
        return False
    
    # FIXME: Implement
    def get_is_in_shopping_cart(self, obj):
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
                )
        return recipe
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ingredients'] = data.pop('ingredients_detail')
        data['tags'] = data.pop('tags_detail')
        return data
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'tags_detail',
            'author',
            'ingredients',
            'ingredients_detail',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
