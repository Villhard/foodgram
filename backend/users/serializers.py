from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    # FIXME: Implement
    @staticmethod
    def get_is_subscribed(obj):
        return False

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'avatar',
            'is_subscribed',
        )


class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'username',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class ExtendedCustomUserSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        from api.serializers import RecipeSerializer
        recipes = obj.recipes.all()
        serializer = RecipeSerializer(recipes, many=True, context=self.context)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
