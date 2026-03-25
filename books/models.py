# books/models.py
from django.db import models
from german_words.models import GermanWord

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название книги")
    author = models.CharField(max_length=200, blank=True, verbose_name="Автор")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Путь к файлу")
    processed = models.BooleanField(default=False, verbose_name="Обработана")

    def __str__(self):
        return self.title

class BookWord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='words')
    word = models.ForeignKey(GermanWord, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=0)

    class Meta:
        unique_together = ('book', 'word')
        verbose_name = "Слово в книге"
        verbose_name_plural = "Слова в книге"

    def __str__(self):
        return f"{self.book.title}: {self.word.german_word} ({self.frequency})"