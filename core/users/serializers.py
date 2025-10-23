from rest_framework import serializers
from .models import User
import os
import time
import hmac
import hashlib


class TelegramAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.CharField(required=False, allow_blank=True)
    auth_date = serializers.IntegerField(required=False)
    hash = serializers.CharField(required=True)

    def validate(self, attrs):
        bot_token = os.environ.get("BOT_TOKEN")

        auth_hash = attrs.get("hash")
        if not auth_hash:
            raise serializers.ValidationError({"error": "Missing hash."})

        pairs = []
        for key, value in attrs.items():
            if key == "hash" or value is None:
                continue
            pairs.append((key, str(value)))
        pairs.sort(key=lambda x: x[0])
        data_check_string = "\n".join([f"{key}={value}" for key, value in pairs])

        secret = hashlib.sha256(bot_token.encode()).digest()
        computed = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
        if computed != auth_hash:
            raise serializers.ValidationError({"error": "Could not validate hash."})

        telegram_id = attrs.get("id")
        if telegram_id is None:
            raise serializers.ValidationError({"error": "Missing Telegram id."})
        username = attrs.get("username") or attrs.get("first_name")
        first_name = attrs.get("first_name")
        user, created = User.objects.update_or_create(
            telegram_id=int(telegram_id), defaults={"username": username, "telegram_name": first_name}
        )

        attrs["user"] = user
        attrs["created"] = created
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "telegram_id", "username", "telegram_name")
