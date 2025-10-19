from rest_framework import serializers
from .models import User


class TelegramAuthSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=False, allow_blank=True)
    hash = serializers.CharField(required=False, allow_blank=True)
    # if needed: first_name = serializers.CharField(required=False)
    # if needed: last_name = serializers.CharField(required=False)

    def validate(self, attrs):
        telegram_id = attrs.get("telegram_id")
        username = attrs.get("username")

        user, created = User.objects.update_or_create(
            telegram_id=telegram_id, defaults={"username": username}
        )

        attrs["user"] = user
        attrs["created"] = created
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "telegram_id", "username", "is_active")
