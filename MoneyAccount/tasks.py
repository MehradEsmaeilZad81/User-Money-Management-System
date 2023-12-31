from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import MoneyAccount, GeneralSource, Subscription, Transaction
from django.utils import timezone


@shared_task
def update_general_sources():
    massage = ""
    for general in GeneralSource.objects.all():
        current_time = timezone.now()
        time_difference = current_time - general.last_updated
        time_difference_seconds = time_difference.total_seconds()
        flag = time_difference_seconds >= (general.deposit_interval*60 - 15)
        if flag:
            general.inventory += general.deposit_amount
            general.last_updated = current_time
            general.save()
            massage += f"{general.name} has been updated!\n"

    return massage


@shared_task
def update_subscription():
    massage = ""
    for subscription in Subscription.objects.all():
        current_time = timezone.now()
        time_difference = current_time - subscription.last_updated
        time_difference_seconds = time_difference.total_seconds()
        flag = time_difference_seconds >= (
            subscription.general_source.deposit_interval*60 - 15)
        if flag:
            if subscription.money_account.balance >= subscription.amounts:
                subscription.money_account.add_expense(subscription.amount)
                subscription.general_source.add_amount(subscription.amount)
                subscription.last_updated = current_time
                subscription.save()
                subscription.money_account.create_transaction(
                    subscription.general_source, subscription.amount, 'D')
                massage += f"Subscription for {subscription.money_account.user.email} - {subscription.general_source.name} has been updated!\n"

            else:
                subscription.delete()
                massage += f"Subscription for {subscription.money_account.user.email} - {subscription.general_source.name} has been deleted!\n"

    return massage
