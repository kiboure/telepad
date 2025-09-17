from rest_framework import permissions


class SoundPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return not obj.is_private or obj.owner == request.user

        if view.action in ["update", "partial_update"]:
            return obj.owner == request.user

        if view.action in ["like", "unlike", "save", "unsave"]:
            return not obj.is_private or obj.owner == request.user

        return False
