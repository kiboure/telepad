from rest_framework.response import Response
from .serializers import TelegramAuthSerializer
from django.contrib.auth import login, logout
from rest_framework import permissions, status, views, generics
from rest_framework_simplejwt.tokens import RefreshToken


class LoginAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TelegramAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        created = serializer.validated_data["created"]

        refresh = RefreshToken.for_user(user)
        data = {
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "created": created,
        }

        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class LogoutAPIView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
