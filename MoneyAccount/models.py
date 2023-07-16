from Authentication.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class MoneyAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expense = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=User)
def create_money_account(sender, instance, created, **kwargs):
    if created:
        MoneyAccount.objects.create(user=instance)


post_save.connect(create_money_account, sender=User)
