from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmation_code = models.CharField(max_length=4, blank=True)

    def str(self):
        return self.username