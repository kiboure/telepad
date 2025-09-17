from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Count, Q, OuterRef, Exists

from .models import Sound
from .serializers import SoundSerializer
from .permissions import SoundPermission
from .tasks.downloads import mock_download


class SoundViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SoundSerializer
    permission_classes = (permissions.IsAuthenticated, SoundPermission)

    # --- Quering Methods ---

    def get_queryset(self):
        user = self.request.user
        foreign_filter = Q(saves=user) if self.action == "list" else Q(is_private=False)

        return (
            Sound.objects.filter(Q(owner=user) | foreign_filter)
            .annotate(
                likes_count=Count("likes"),
                is_saved=Exists(user.saved_sounds.filter(pk=OuterRef("pk"))),
            )
            .order_by("-id")
        )

    # --- Other ---

    def get_serializer_context(self):
        return {"request": self.request}

    # --- Custom Actions ---

    @action(detail=False, methods=["get"])
    def list_all(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    # Likes
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        sound = self.get_object()
        sound.likes.add(request.user)
        return Response({"detail": f"Liked {sound.name}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        sound = self.get_object()
        sound.likes.remove(request.user)
        return Response({"detail": f"Unliked {sound.name}"}, status=status.HTTP_200_OK)

    # Saves
    @action(detail=True, methods=["post"])
    def save(self, request, pk=None):
        sound = self.get_object()
        if sound.owner == request.user:
            return Response(
                {"detail": "You cannot save your own sound."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sound.saves.add(request.user)
        return Response({"detail": f"Saved {sound.name}."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unsave(self, request, pk=None):
        sound = self.get_object()
        sound.saves.remove(request.user)
        return Response({"detail": f"Removed {sound.name}."}, status=status.HTTP_200_OK)


@api_view(["POST"])
def download(request):
    url = request.data.get("url")
    task = mock_download.delay(request.user.id, url)
    return Response(
        {"detail": f"Started task with id {task.id}."},
        status=status.HTTP_202_ACCEPTED,
    )
