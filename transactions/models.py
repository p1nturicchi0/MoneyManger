from django.contrib.auth.models import User
from django.db import models


transaction_option = (
    ('income', 'Income'),
    ('expense', 'Expense'),
)


class Transaction(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    transaction_type = models.CharField(max_length=7, choices=transaction_option)
    transaction_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

class Limit(models.Model):

    limit = models.DecimalField(decimal_places=2, max_digits=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.limit}'