from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    # FIXME: Настроить логику определения подписки
    def get_is_subscribed(self, obj):
        return False

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'username', 'avatar', 'is_subscribed')


class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}
