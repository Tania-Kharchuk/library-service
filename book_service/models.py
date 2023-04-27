from django.db import models


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=70)
    author = models.CharField(max_length=70)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.title
