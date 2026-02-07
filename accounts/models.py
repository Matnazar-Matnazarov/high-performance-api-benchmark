# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrator"
    SHOPKEEPER = "SHOPKEEPER", "Shopkeeper"
    CUSTOMER = "CUSTOMER", "Customer"


class User(AbstractUser):
    role = models.CharField(
        max_length=255,
        choices=Role.choices,
        default=Role.CUSTOMER,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.username

    def get_role_display(self):
        return self.role
