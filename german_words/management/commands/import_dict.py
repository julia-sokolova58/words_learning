import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from german_words.models import GermanWord


class Command(BaseCommand):
    help = 'Import German words from CSV'

    def handle(self, *args, **options):
        csv_file = os.path.join(settings.BASE_DIR, 'static', 'data', 'cleaned_words.csv')
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                GermanWord.objects.get_or_create(
                    german_word=row['Немецкое слово'].strip("'\""),
                    defaults={'russian_translation': row['Перевод на русский'].strip("'\"")}
                )
        
        self.stdout.write(self.style.SUCCESS('Import complete!'))