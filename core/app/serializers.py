from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from taggit.models import Tag
from .models import Sound


class SoundSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    likes_count = serializers.IntegerField(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Sound
        fields = (
            "id",
            "owner",
            "name",
            "file_path",
            "file_id",
            "duration",
            "tags",
            "likes_count",
            "is_saved",
            "is_liked",
            "is_private",
        )
        read_only_fields = [
            "id",
            "owner",
            "file_path",
            "file_id",
            "duration",
            "likes_count",
            "is_saved",
        ]

    def validate_tags(self, value):
        if value is None:
            return value
        if len(value) > 10:
            raise serializers.ValidationError("Sound cant contain more than 10 tags.")
        return value


class DownloadSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048, required=True)


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, allow_empty_file=False)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)
