from django.contrib.auth.models import User
import django_filters
from django_filters import rest_framework as rest_filters


class UserFilter(rest_filters.FilterSet):
    username = django_filters.CharFilter(name='username', lookup_expr='icontains')
    email = django_filters.CharFilter(name='email', lookup_expr='icontains')
    summoner = django_filters.CharFilter(name='summoner__summoner_name', lookup_expr='icontains', label='Summoner name contains')

    class Meta:
        model = User
        fields = ['username', 'email', 'summoner']