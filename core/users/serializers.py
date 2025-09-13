from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from django.contrib.auth import authenticate


class SignupSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(required=False, max_length=255)

    class Meta:
        model = User
        fields = ("telegram_id", "username")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        telegram_id = attrs.get("telegram_id")
        request = self.context.get("request")
        user = authenticate(request=request, telegram_id=telegram_id)

        if not user:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials", code="authorization"
            )

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "telegram_id", "username", "is_active")
