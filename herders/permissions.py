from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from herders.models import Summoner


class IsSelfOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            is_self = request.user == obj or request.user.is_superuser
        else:
            is_self = False

        if request.method in permissions.SAFE_METHODS and not (
            is_self or
            obj.summoner.public or
            request.user.is_superuser
        ):
            raise PermissionDenied(detail='Profile is not public.')

        return is_self or (request.method in permissions.SAFE_METHODS and obj.summoner.public)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        username = view.kwargs.get('user_pk', None)

        if username is None:
            # Doc generation doesn't supply a username, but permissions need to be true to generate all actions correctly
            # All URL endpoints that use this permission will supply a username
            return True

        try:
            summoner = Summoner.objects.select_related('user').get(user__username=username)
        except Summoner.DoesNotExist:
            raise NotFound()
        else:
            is_owner = summoner.user == request.user

            if request.method in permissions.SAFE_METHODS and not (
                is_owner or
                summoner.public or
                request.user.is_superuser
            ):
                raise PermissionDenied(detail='Profile is not public.')

            return (
                is_owner or
                (summoner.public and request.method in permissions.SAFE_METHODS) or
                request.user.is_superuser
            )

    def has_object_permission(self, request, view, obj):
        username = view.kwargs.get('user_pk', None)

        if request.user.is_authenticated:
            is_owner = (
                obj.owner == request.user.summoner and
                username == request.user.username
            ) or request.user.is_superuser
        else:
            is_owner = False

        return (
            is_owner or
            (request.method in permissions.SAFE_METHODS and obj.owner.public) or
            request.user.is_superuser
        )
