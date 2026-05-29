from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('debit', 'Дебет'),
        ('credit', 'Кредит'),
    ]

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return f"{self.description} - {self.amount}"