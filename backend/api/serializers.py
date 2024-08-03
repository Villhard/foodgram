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
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)
    ingredients_detail = RecipeIngredientReadSerializer(
        source='recipeingredient_set', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    def validate(self, data):
        required_fields = [
            'tags',
            'ingredients',
        ]
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(
                    {field: 'This field is required'}
                )
        return data

    @staticmethod
    def validate_ingredients(value):
        if not value:
            raise serializers.ValidationError(
                'Для создания рецепта необходим хотя бы один ингредиент'
            )
        ingredients = []
        for item in value:
            ingredient = item['ingredient']
            if ingredient in ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            ingredients.append(ingredient)
        return value

    @staticmethod
    def validate_tags(value):
        if not value:
            raise serializers.ValidationError(
                'Для создания рецепта необходим хотя бы один тег'
            )
        if len(value) > len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться')
        return value

    @staticmethod
    def validate_image(value):
        if not value:
            raise serializers.ValidationError(
                'Для создания рецепта необходимо загрузить изображение'
            )
        return value

    @staticmethod
    def set_ingredients_and_tags(recipe, ingredients, tags):
        recipe.tags.set(tags)
        recipe.recipeingredient_set.all().delete()
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )

        self.set_ingredients_and_tags(recipe, ingredients, tags)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)

        self.set_ingredients_and_tags(instance, ingredients, tags)

        return instance

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


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
