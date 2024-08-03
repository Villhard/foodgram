import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from csv file'
    ingredients_file = 'recipes/management/commands/ingredients.csv'
    fields = ('name', 'measurement_unit')

    def handle(self, *args, **options):
        with open(self.ingredients_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, fieldnames=self.fields)
            for row in reader:
                Ingredient.objects.get_or_create(**row)
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены'))
