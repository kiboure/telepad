from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, telegram_id: int, username: str = None):
        if not telegram_id:
            raise ValueError("Users must have a telegram id")

        user = self.model(telegram_id=telegram_id, username=username)
        user.set_unusable_password()
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "telegram_id"
    REQUIRED_FIELDS = []

    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.telegram_id} ({self.username or ''})"
