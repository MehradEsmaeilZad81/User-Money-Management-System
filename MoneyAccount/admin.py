from django.contrib import admin
from .models import MoneyAccount, GeneralSource

# Register your models here.

admin.site.register(MoneyAccount)
admin.site.register(GeneralSource)