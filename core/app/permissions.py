from rest_framework import permissions
from django.conf import settings


class SoundPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return not obj.is_private or obj.owner == request.user

        if view.action in ["update", "partial_update"]:
            return obj.owner == request.user

        if view.action in ["like", "unlike", "save", "unsave"]:
            return not obj.is_private or obj.owner == request.user

        # Allow owner to toggle visibility
        if view.action in ["hide", "unhide"]:
            return obj.owner == request.user

        return False


class IsBotPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.headers.get("Authorization") == f"Bot {settings.BOT_API_KEY}"
