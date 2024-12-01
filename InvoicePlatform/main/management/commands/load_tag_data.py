import csv
import os
from django.core.management.base import BaseCommand, CommandError
from main.models import ItemBigTag, ItemSmallTag


class Command(BaseCommand):
    help = 'Load item tags and items from CSV file'

    def handle(self, *args, **kwargs):
        path = os.path.join(os.path.dirname(__file__), 'Tag.csv')
        if not os.path.exists(path):
            raise CommandError(f'File "{path}" does not exist')

        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for header in headers:
                ItemBigTag.objects.get_or_create(name=header)
            for row in reader:
                for big, small in zip(headers, row):
                    if small:
                        bigTag = ItemBigTag.objects.get(name=big)
                        smallTag, created = ItemSmallTag.objects.get_or_create(name=small, bigTag=bigTag)
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f'SmallTag "{smallTag.name}" in "{bigTag.name}" created')
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'SmallTag "{smallTag.name}" in "{bigTag.name}" already exists')
                            )

        self.stdout.write(self.style.SUCCESS('Data successfully loaded'))
