from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import MoneyAccount, GeneralSource
from django.utils import timezone

@shared_task
def print_last_updated():
    return "Successfull!"