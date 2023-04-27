from django.db import models

from borrowing_service.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(max_length=7, choices=Status.choices)
    type = models.CharField(max_length=7, choices=Type.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=256)
    money_to_pay = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.money_to_pay}USD {self.type} in status {self.status}"
