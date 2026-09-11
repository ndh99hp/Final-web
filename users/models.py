from django.contrib.auth.models import AbstractUser
from django.db import models
class Country(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
    def __str__(self):
        return self.name
class User(AbstractUser):
    LEVEL_CHOICES = (
        (0, 'User'),
        (1, 'Staff'),
        (2, 'Admin'),
    )
    level = models.IntegerField(choices=LEVEL_CHOICES, default=0)
    id_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username