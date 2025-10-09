from django.db import models
from taggit.managers import TaggableManager
from django.contrib.postgres.indexes import GinIndex

from users.models import User


class Sound(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sounds",
    )
    name = models.CharField(max_length=255)
    file_path = models.FileField()
    file_id = models.CharField()
    duration = models.IntegerField()
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
    is_private = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.name}"

    class Meta:
        indexes = [
            GinIndex(
                fields=["name"],
                name="sound_name_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]
