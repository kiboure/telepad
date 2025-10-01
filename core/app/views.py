# -- IMPORTS --
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action, api_view, parser_classes

from django.db.models import Count, Exists, Q, OuterRef
from django.core.files.storage import default_storage

from .models import Sound
from .serializers import SoundSerializer, DownloadSerializer, UploadSerializer
from .permissions import SoundPermission
from .tasks.downloads import download_sound, upload_sound


# -- PAGINATION --
class Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# -- SOUNDS MODEL --
class SoundViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SoundSerializer
    pagination_class = Pagination
    permission_classes = (permissions.IsAuthenticated, SoundPermission)

    # --- Quering Methods ---
    def get_queryset(self):
        user = self.request.user
        qs = Sound.objects.filter(is_active=True).annotate(likes_count=Count("likes"))

        if self.action == "list":
            qs = qs.filter(saves=user)
        else:
            qs = qs.filter(Q(owner=user) | Q(is_private=False)).annotate(
                is_saved=Exists(user.saved_sounds.filter(pk=OuterRef("pk"))),
            )

        return qs.order_by("-id")

    # --- Other ---
    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["get"], url_path="search")
    def search_all(self, request):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # --- Likes ---
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        sound = self.get_object()
        sound.likes.add(request.user)
        return Response(
            {"method": "Like", "sound_name": sound.name}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        sound = self.get_object()
        sound.likes.remove(request.user)
        return Response(
            {"method": "Unlike", "sound_name": sound.name}, status=status.HTTP_200_OK
        )

    # --- Saves ---
    @action(detail=True, methods=["post"])
    def save(self, request, pk=None):
        sound = self.get_object()
        sound.saves.add(request.user)
        return Response(
            {"method": "Save", "sound_name": sound.name}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def unsave(self, request, pk=None):
        sound = self.get_object()
        sound.saves.remove(request.user)
        method = "Unsave"

        if not sound.saves.exists():
            sound.is_active = False
            sound.save(update_fields=["is_active"])
            method = "Delete"

        return Response(
            {"method": method, "sound_name": sound.name},
            status=status.HTTP_200_OK,
        )


# -- SOUND FILES --
@api_view(["POST"])
def download(request):
    serializer = DownloadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    url = serializer.validated_data.get("url")

    task = download_sound.delay(request.user.id, url)

    return Response(
        {"method": "Download", "detail": "Task started", "task_id": task.id},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload(request):
    serializer = UploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_file = serializer.validated_data["file"]

    try:
        temp_file = default_storage.save(validated_file.name, validated_file)
    except Exception as error:
        return Response(
            {"method": "Upload", "detail": f"Error saving file: {error}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    task = upload_sound.delay(request.user.id, temp_file, validated_file.name)

    return Response(
        {"method": "Upload", "detail": "Task started", "task_id": task.id},
        status=status.HTTP_202_ACCEPTED,
    )
