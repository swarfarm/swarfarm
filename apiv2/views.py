from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission, AllowAny, DjangoModelPermissionsOrAnonReadOnly

from news.models import *
from .serializers import *
from .filters import *


# JWT response to include user data
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


# DRF permissions
class ViewUserList(BasePermission):
    def has_permission(self, request, view):
        # Only allow if retrieving single instance or is admin
        return request.user.is_superuser or view.action == 'retrieve'

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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_class = UserFilter

    def get_permissions(self):
        if self.request.method == 'POST':
            return (AllowAny(), )
        else:
            return (ViewUserList(), )


# News
class ArticlePagination(LimitOffsetPagination):
    default_limit = 10


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination