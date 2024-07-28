from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ('id',)
        verbose_name = 'Избранное'
