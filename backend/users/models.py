from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254, unique=True, blank=False, null=False
    )
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    avatar = models.ImageField(upload_to='media/users/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    follower = models.ForeignKey(
        CustomUser, related_name='following', on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        CustomUser, related_name='followers', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ('id',)
