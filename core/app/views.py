# -- IMPORTS --
import os
from django.core.checks import Tags
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action, api_view, parser_classes

from django.db.models import Count, Exists, Q, OuterRef
from django.core.files.storage import default_storage
from taggit.models import Tag

from .models import Sound
from .serializers import (
    SoundSerializer,
    DownloadSerializer,
    UploadSerializer,
    TagSerializer,
)
from .permissions import SoundPermission
from .tasks.downloads import download_sound, upload_sound
from telepad.settings import MEDIA_ROOT
from telepad.celery import app as celery_app
from django.middleware.csrf import get_token


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

    # --- Queryset constructor ---
    def get_queryset(self):
        user = self.request.user
        qs = (
            Sound.objects.filter(is_active=True)
            .annotate(
                likes_count=Count("likes"),
                is_saved=Exists(user.saved_sounds.filter(pk=OuterRef("pk"))),
                is_liked=Exists(user.liked_sounds.filter(pk=OuterRef("pk"))),
            )
        )

        # Tags
        tag_names = self.request.query_params.getlist("tags")
        if tag_names:
            for tag in tag_names:
                qs = qs.filter(tags__name=tag)
            qs = qs.distinct()

        # Searching
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        # Access
        if self.action == "list":
            qs = qs.filter(saves=user)
        else:
            qs = qs.filter(Q(owner=user) | Q(is_private=False))

        return qs.order_by("-id")

    # --- Other ---
    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
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
        temp_name = default_storage.save(validated_file.name, validated_file)
        temp_file = os.path.join(MEDIA_ROOT, temp_name)
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


# -- TAGS --
@api_view(["GET"])
def tags(request):
    tags_queryset = Tag.objects.all()
    serializer = TagSerializer(tags_queryset, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


# -- TASKS STATUS --
@api_view(["GET"])
def task_status(request, task_id: str):
    result = celery_app.AsyncResult(task_id)
    payload = {
        "task_id": task_id,
        "state": result.state,
        "status": str(result.info) if result.info else None,
        "result": result.result if result.successful() else None,
    }
    return Response(payload, status=status.HTTP_200_OK)


# -- CSRF --
@api_view(["GET"])
def csrf_token(request):
    token = get_token(request)
    return Response({"csrfToken": token}, status=status.HTTP_200_OK)
