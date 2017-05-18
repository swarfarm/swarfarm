from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission, AllowAny, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse
from refreshtoken.models import RefreshToken

from news.models import *
from .serializers import *
from .filters import *


# JWT response to include user data
def jwt_response_payload_handler(token, user=None, request=None):
    payload = {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }

    app = 'swarfarm'

    try:
        refresh_token = user.refresh_tokens.get(app=app).key
    except RefreshToken.DoesNotExist:
        # Create it
        refresh_token = user.refresh_tokens.create(app=app).key

    payload['refresh_token'] = refresh_token
    return payload


# DRF permissions
class ViewUserList(BasePermission):
    def has_permission(self, request, view):
        # Only allow if retrieving single instance or is admin
        return request.user.is_superuser or (view.action in ['retrieve', 'list'] and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class IsStaffOrOwner(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.owner == request.user


# User / Auth
class UserPagination(LimitOffsetPagination):
    default_limit = 25


class UserViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given user.

    list:
    Return a list of all the existing users. Requires admin permissions, otherwise only returns yourself.

    create:
    Create a new user instance.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_class = UserFilter
    lookup_field = 'username'

    def get_permissions(self):
        if self.request.method == 'POST':
            return (AllowAny(), )
        else:
            return (ViewUserList(), )

    def get_queryset(self):
        queryset = super(UserViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        elif self.request.user.is_authenticated:
            return queryset.filter(pk=self.request.user.pk)
        else:
            return queryset.none()
