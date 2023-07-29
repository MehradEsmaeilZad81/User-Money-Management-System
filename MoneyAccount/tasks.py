from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import MoneyAccount, GeneralSource
from django.utils import timezone

@shared_task
def update_general_sources():
    for general in GeneralSource.objects.all():
        current_time = timezone.now()
        time_difference = current_time - general.last_updated
        time_difference_seconds = time_difference.total_seconds()
        flag = time_difference_seconds >= (general.deposit_interval*60 - 15)
        if flag:
            general.inventory += general.deposit_amount
            general.last_updated = current_time
            general.save()

    return "Successfull!"