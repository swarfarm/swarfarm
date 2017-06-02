from rest_framework import permissions
from rest_framework.compat import is_authenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from herders.models import Summoner


class IsSelfOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            is_self = request.user == obj or request.user.is_superuser
        else:
            is_self = False

        if not is_self and not obj.summoner.public and not request.user.is_superuser:
            raise PermissionDenied(detail='Profile is not public.')

        return is_self or (request.method in permissions.SAFE_METHODS and obj.summoner.public)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        summoner_name = view.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            # Profile specific check
            try:
                summoner = Summoner.objects.select_related('user').get(user__username=summoner_name)
            except Summoner.DoesNotExist:
                raise NotFound()
            else:
                is_owner = summoner.user == request.user

                if not is_owner and not summoner.public and not request.user.is_superuser:
                    raise PermissionDenied(detail='Profile is not public.')

                return (
                    is_owner or
                    (summoner.public and request.method in permissions.SAFE_METHODS) or
                    request.user.is_superuser
                )
        else:
            # Not profile specific - read only allowed, get_queryset will filter to public items only.
            return request.method in permissions.SAFE_METHODS or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if is_authenticated(request.user):
            is_owner = obj.owner == request.user.summoner or request.user.is_superuser
        else:
            is_owner = False

        return (
            is_owner or
            (request.method in permissions.SAFE_METHODS and obj.owner.public) or
            request.user.is_superuser
        )
