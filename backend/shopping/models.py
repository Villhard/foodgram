from django.db import models
from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart', verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ('id',)
        verbose_name = 'Корзина'
