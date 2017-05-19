from rest_framework.permissions import BasePermission


# DRF permissions
class ViewUserListPermission(BasePermission):
    def has_permission(self, request, view):
        # Only allow if retrieving single instance or is admin
        return request.user.is_superuser or (view.action in ['retrieve', 'list'] and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj == request.user
