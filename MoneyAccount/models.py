from Authentication.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import schedule
import time
# Create your models here.


class MoneyAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=10000.00)
    income = models.DecimalField(
        max_digits=10, decimal_places=2, default=10000.00)
    expense = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.email

    def has_sufficient_balance(self, amount):
        return self.balance >= amount

    def calculate_net_balance(self):
        return self.income - self.expense

    def add_income(self, amount):
        self.income += amount
        self.save()

    def add_expense(self, amount):
        self.expense += amount
        self.save()

    def get_account_details(self):
        return {
            'user_email': self.user.email,
            'balance': self.balance,
            'income': self.income,
            'expense': self.expense
        }


class GeneralSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    inventory = models.DecimalField(
        max_digits=10, decimal_places=2, default=100000.00)
    coefficient = models.DecimalField(
        max_digits=2, decimal_places=2, default=0.50)
    deposit_interval = models.PositiveIntegerField(default=1)
    deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=1000.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_money_account(sender, instance, created, **kwargs):
    # Create a money account for the newly registered user.
    if created:
        MoneyAccount.objects.create(user=instance)

# Connect the signal to the function to automatically create money accounts for new users.
post_save.connect(create_money_account, sender=User)
