from django.contrib import admin
from .models import MoneyAccount, GeneralSource, Subscription, Transaction, UserTransaction

# Register your models here.

admin.site.register(MoneyAccount)
admin.site.register(GeneralSource)
admin.site.register(Subscription)
admin.site.register(Transaction)
admin.site.register(UserTransaction)
