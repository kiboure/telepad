from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import Sound
from app.serializers import SoundSerializer
from app.permissions import IsBotPermission


class BotListView(APIView):
    permission_classes = [IsBotPermission]

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response(
                {"detail": "Field telegram_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            Sound.objects.filter(
                Q(owner__telegram_id=telegram_id) | Q(saves__telegram_id=telegram_id)
            )
            .distinct()
            .order_by("-id")
        )

        serializer = SoundSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
