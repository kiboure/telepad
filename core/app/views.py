from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, OuterRef, Exists

from .models import Sound
from .serializers import SoundSerializer


class SoundViewSet(viewsets.ModelViewSet):
    serializer_class = SoundSerializer
    permission_classes = (permissions.IsAuthenticated,)
    forbidden_message = Response(
        {"detail": "You are not the owner of this sound."},
        status=status.HTTP_403_FORBIDDEN,
    )

    # Default list query
    def get_queryset(self):
        return (
            Sound.objects.filter(owner=self.request.user)
            .annotate(like_count=Count("likes"))
            .order_by("-id")
        )

    # ViewSet methods overrides
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        sound = self.get_object()
        if sound.owner != request.user:
            return self.forbidden_message
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        sound = self.get_object()
        if sound.owner != request.user:
            return self.forbidden_message
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        sound = self.get_object()
        if sound.owner != request.user:
            return self.forbidden_message
        return super().destroy(request, *args, **kwargs)

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

    # Global list
    @action(detail=False, methods=["get"])
    def list_all(self, request):
        user = request.user

        subquery = user.saved_sounds.filter(pk=OuterRef("pk"))
        queryset = (
            Sound.objects.filter(Q(is_private=False) | Q(owner=user))
            .annotate(
                like_count=Count("likes"),
                is_saved=Exists(subquery),
            )
            .select_related("owner")
            .order_by("-id")
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
