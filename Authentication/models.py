from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True, null=False, blank=False)
    username = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
