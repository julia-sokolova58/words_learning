from django.db import models


class GermanWord(models.Model):
    german_word = models.CharField(
        max_length=200,
        verbose_name="Немецкое слово",
        unique=True
    )
    russian_translation = models.CharField(
        max_length=200,
        verbose_name="Перевод на русский"
    )

    def __str__(self):
        return f"{self.german_word} - {self.russian_translation[:50]}"
