from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('PROVIDER', 'Proveedor'),
        ('CLIENT', 'Cliente'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PROVIDER')
    phone = models.CharField(max_length=20, blank=True)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return self.get_full_name() or self.username
