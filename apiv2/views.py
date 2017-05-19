from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from refreshtoken.models import RefreshToken

from news.models import *
from apiv2.serializers import *
from apiv2.filters import *
from apiv2.permissions import *
from apiv2.pagination import *


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


# User / Auth
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
            return (ViewUserListPermission(),)

    def get_queryset(self):
        queryset = super(UserViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        elif self.request.user.is_authenticated:
            return queryset.filter(pk=self.request.user.pk)
        else:
            return queryset.none()
