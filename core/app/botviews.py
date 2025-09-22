from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Sound, User
from .serializers import SoundSerializer
from .permissions import IsBotPermission


class BotListView(APIView):
    permission_classes = [IsBotPermission]

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response(
                {"detail": "Field telegram_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_BAD_REQUEST,
            )

        queryset = Sound.objects.filter(Q(owner=user) | Q(saves=user)).order_by("-id")

        serializer = SoundSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
