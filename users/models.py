from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from rest_framework_api_key.models import AbstractAPIKey
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, name, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(name=name,email=email,)
        user.set_password(password)
        user.save(self._db)
        return user

    def create_superuser(self, name, email, password=None):
        user = self.create_user(name=name, email=email, password=password,)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name


class UserAPIKey(AbstractAPIKey):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_api_key(sender, instance, created, **kwargs):
    api_key, key = UserAPIKey.objects.create_key(name=instance.name, user_id=instance.id)