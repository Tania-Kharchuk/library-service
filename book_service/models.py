from django.db import models
from djmoney.models.fields import MoneyField


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=70)
    author = models.CharField(max_length=70)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = MoneyField(
        decimal_places=2,
        default=0,
        default_currency="USD",
        max_digits=11,
    )

    def __str__(self):
        return self.title
