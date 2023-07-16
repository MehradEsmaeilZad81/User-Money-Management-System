from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=50, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
