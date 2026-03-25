from django.db import models


class GermanWord(models.Model):
    german_word = models.CharField(max_length=500, unique=True)
    russian_translation = models.TextField()
    frequency_score = models.FloatField(default=0.0, verbose_name="Частотность")

    def __str__(self):
        return f"{self.german_word} - {self.russian_translation[:50]}"
