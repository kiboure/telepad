from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from .models import Sound
from .serializers import SoundSerializer


class SoundViewSet(viewsets.ModelViewSet):
    serializer_class = SoundSerializer
    permission_classes = (permissions.IsAuthenticated,)
    forbidden_message = Response(
        {"detail": "You are not the owner of this sound."},
        status=status.HTTP_403_FORBIDDEN,
    )

    def get_queryset(self):
        return Sound.objects.filter(user=self.request.user).annotate(
            like_count=Count("likes")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        sound = self.get_object()
        if sound.user != request.user:
            return self.forbidden_message
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        sound = self.get_object()
        if sound.user != request.user:
            return self.forbidden_message
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        sound = self.get_object()
        if sound.user != request.user:
            return self.forbidden_message
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        sound = self.get_object()
        sound.likes.add(request.user)
        return Response({"status": f"Liked {sound.name}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        sound = self.get_object()
        sound.likes.remove(request.user)
        return Response({"status": f"Unliked {sound.name}"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def list_all(self, request):
        queryset = Sound.objects.filter(is_private=False).annotate(
            like_count=Count("likes")
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
