from rest_framework.pagination import LimitOffsetPagination


class UserPagination(LimitOffsetPagination):
    default_limit = 25
