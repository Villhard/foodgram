from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email',
    )
    first_name = models.CharField(
        max_length=150, blank=False, null=False, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150, blank=False, null=False, verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='media/users/', blank=True, null=True, verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        CustomUser,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'], name='unique_subscription'
            )
        ]
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
