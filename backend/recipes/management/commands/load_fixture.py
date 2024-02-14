import csv
import os
from django.conf import settings

from django.core.management.base import BaseCommand
from progress.bar import IncrementalBar
from recipes.models import Ingredient, Tag


def ingredient_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


def tag_create(row):
    Tag.objects.get_or_create(
        name=row[0],
        color=row[1],
        slug=row[2]
    )


class Command(BaseCommand):
    help = 'Load ingredients and tags to DB'

    def handle(self, *args, **options):
        ingredient_path = os.path.join(settings.BASE_DIR, 'ingredients.csv')
        with open(ingredient_path, 'r', encoding='utf-8') as file:
            ingredient_reader = csv.reader(file)
            ingredient_row_count = sum(1 for row in ingredient_reader)
        with open(ingredient_path, 'r', encoding='utf-8') as file:
            ingredient_reader = csv.reader(file)
            ingredient_bar = IncrementalBar('ingredients.csv'.ljust(17), max=ingredient_row_count)
            next(ingredient_reader)
            for row in ingredient_reader:
                ingredient_bar.next()
                ingredient_create(row)
            ingredient_bar.finish()

        tag_path = os.path.join(settings.BASE_DIR, 'tags.csv')
        with open(tag_path, 'r', encoding='utf-8') as file:
            tag_reader = csv.reader(file)
            tag_row_count = sum(1 for row in tag_reader)
        with open(tag_path, 'r', encoding='utf-8') as file:
            tag_reader = csv.reader(file)
            tag_bar = IncrementalBar('tags.csv'.ljust(17), max=tag_row_count)
            next(tag_reader)
            for row in tag_reader:
                tag_bar.next()
                tag_create(row)
            tag_bar.finish()

        self.stdout.write('The ingredients and tags have been loaded successfully.')
