import os
from django.core.management.base import BaseCommand, CommandError
from books.models import Book, BookWord
from german_words.models import GermanWord
from services.text_processor import get_word_frequencies

class Command(BaseCommand):
    help = 'Parse a book file and extract words into BookWord'

    def add_arguments(self, parser):
        parser.add_argument('--book_id', type=int, help='ID of the book to parse. If not given, the first book is used.')

    def handle(self, *args, **options):
        book_id = options.get('book_id')
        if book_id:
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                raise CommandError(f'Book with id {book_id} does not exist.')
        else:
            book = Book.objects.first()
            if not book:
                raise CommandError('No books found in database.')

        self.stdout.write(f'Parsing book: {book.title} (ID: {book.id})')

        if not book.file_path or not os.path.exists(book.file_path):
            raise CommandError(f'File not found: {book.file_path}')

        with open(book.file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        self.stdout.write('Extracting words from text...')
        word_freq = get_word_frequencies(text)

        self.stdout.write(f'Found {len(word_freq)} unique word forms.')

        created_count = 0
        for word_form, freq in word_freq.items():
            german_word = GermanWord.objects.filter(german_word=word_form).first()
            if german_word:
                book_word, created = BookWord.objects.get_or_create(
                    book=book,
                    word=german_word,
                    defaults={'frequency': freq}
                )
                if not created:
                    book_word.frequency = freq
                    book_word.save()
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed book "{book.title}". '
            f'Linked {created_count} words out of {len(word_freq)} unique word forms.'
        ))

        book.processed = True
        book.save()