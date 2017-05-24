from rest_framework import permissions


class IsSelfOrPublic(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        is_self = request.user == obj or request.user.is_superuser

        return is_self or (request.method in permissions.SAFE_METHODS and obj.public)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user or request.user.is_superuser

        return is_owner or (request.method in permissions.SAFE_METHODS and obj.owner.public)
