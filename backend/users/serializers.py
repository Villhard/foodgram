from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    # FIXME: Настроить логику определения подписки
    def get_is_subscribed(self, obj):
        return False

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'username')


class CustomCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}
