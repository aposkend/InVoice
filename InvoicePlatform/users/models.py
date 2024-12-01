from django.db import models

# Create your models here.
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import IntegerField


class User(AbstractUser):
    username = models.CharField(max_length=30, blank=True, null=True, default=None)
    is_active = models.BooleanField(blank=True, null=True, default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    email = models.CharField(max_length=30, blank=True, null=True, default=None)
