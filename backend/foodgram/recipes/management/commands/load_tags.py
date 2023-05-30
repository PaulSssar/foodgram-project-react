import csv

from django.core.management.base import BaseCommand
from recipes.models import Tags


class Command(BaseCommand):
    help = 'Загрузка ингредиентов'

    def handle(self, *args, **options):
        with open(
            './data/tag.csv', 'r', encoding='utf-8'
        ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            tags = []
            for row in csv_reader:
                try:
                    create_tags = Tags(
                        name=row[0],
                        color=row[1],
                        slug=row[2],
                    )
                    tags.append(create_tags)
                except ValueError:
                    print('Неверные данные')
            Tags.objects.bulk_create(tags)
