from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Sound


class SoundSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Sound
        fields = ("id", "name", "file", "tags", "likes_count", "created_at")
        read_only_fields = ["id", "likes_count", "created_at"]

    # def create(self, validated_data):
    #     user = self.context["request"].user
    #     return Sound.objects.create(user=user, **validated_data)
