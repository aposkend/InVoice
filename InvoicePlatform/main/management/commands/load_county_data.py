import csv
import os
from django.core.management.base import BaseCommand, CommandError
from main.models import County, District


class Command(BaseCommand):
    help = 'Load data from CSV file into County and District models'

    def handle(self, *args, **kwargs):
        path = os.path.join(os.path.dirname(__file__), 'TW.csv')
        if not os.path.exists(path):
            raise CommandError(f'File "{path}" does not exist')
        with open(path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for header in headers:
                county, created = County.objects.get_or_create(name=header)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'County "{county.name}" created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'County "{county.name}" already exists'))

            for row in reader:
                for county_name, district_name in zip(headers, row):
                    if district_name:
                        county = County.objects.get(name=county_name)
                        district, created = District.objects.get_or_create(name=district_name, county=county)
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f'District "{district.name}" in "{county.name}" created')
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'District "{district.name}" in "{county.name}" already exists')
                            )

            self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
