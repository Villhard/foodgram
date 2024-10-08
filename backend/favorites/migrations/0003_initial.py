# Generated by Django 3.2.3 on 2024-08-03 19:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('favorites', '0002_favorite_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='favorites',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пользователь',
            ),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite'
            ),
        ),
    ]
