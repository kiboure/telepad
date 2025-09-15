from django.db import models
from taggit.managers import TaggableManager
from users.models import User


class Sound(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sounds",
    )
    name = models.CharField(max_length=255)
    file = models.FileField()
    tags = TaggableManager(blank=True)
    likes = models.ManyToManyField(
        User,
        related_name="liked_sounds",
        blank=True,
    )
    saves = models.ManyToManyField(
        User,
        related_name="saved_sounds",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.name}"
