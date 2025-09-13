from rest_framework.response import Response
from .serializers import (
    SignupSerializer,
    LoginSerializer,
)
from django.contrib.auth import login, logout
from rest_framework import permissions, status, generics, views


class SignupAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user, backend="users.backends.TelegramAuthBackend")

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"detail": "Successfully logged out"},
            status=status.HTTP_200_OK,
        )
