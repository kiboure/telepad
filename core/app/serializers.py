from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Sound


class SoundSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Sound
        fields = ("id", "owner", "name", "file", "tags", "likes_count")
        read_only_fields = ["id", "owner", "likes_count"]
