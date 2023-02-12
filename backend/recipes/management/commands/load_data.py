import csv
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка базы ингредиентов из Json или csv файла'

    def handle(self, *args, **options):
        # with open(
        #         '../data/ingredients.json',
        #         encoding='utf-8',
        # ) as json_file:
        #     data = json.load(json_file)
        #     for ingredient in data['ingredients']:
        #         Ingredient.objects.get_or_create(
        #             name=ingredient['name'],
        #             measurement_unit=ingredient['measurement_unit'],
        #         )
        #
        # self.stdout.write(self.style.SUCCESS('Successfully load json'))

        with open(
                '../data/ingredients.csv',
                encoding='utf-8',
        ) as csv_file:
            reader = csv.reader(csv_file)
            for name, measurement_unit in reader:
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

        self.stdout.write(self.style.SUCCESS('Successfully load csv'))
