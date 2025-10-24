from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, telegram_id: int, first_name: str, username: str = None):
        if not telegram_id:
            raise ValueError("telegram_id is required.")
        if not first_name:
            raise ValueError("first_name is required.")

        user = self.model(telegram_id=telegram_id, username=username, first_name=first_name)
        user.set_unusable_password()
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "telegram_id"
    REQUIRED_FIELDS = []

    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.telegram_id} ({self.username or self.first_name})"
