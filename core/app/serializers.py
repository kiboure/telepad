from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import Sound


class SoundSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    likes_count = serializers.IntegerField(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Sound
        fields = (
            "id",
            "owner",
            "name",
            "file_path",
            "duration",
            "tags",
            "likes_count",
            "is_saved",
            "is_private",
        )
        read_only_fields = [
            "id",
            "owner",
            "file_path",
            "duration",
            "likes_count",
            "is_saved",
        ]


class DownloadSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048, required=True)


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, allow_empty_file=False)
