from django.db.models import Q

from rest_framework import viewsets, filters

from herders.models import Storage, MonsterInstance, RuneInstance, RuneCraftInstance
from herders.serializers import *
from herders.pagination import *
from herders.permissions import *


class SummonerViewSet(viewsets.ModelViewSet):
    queryset = Summoner.objects.all().select_related('user')
    serializer_class = SummonerSerializer
    pagination_class = SummonerPagination
    permission_classes = [IsStaffOrOwner]
    lookup_field = 'user__username'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super(SummonerViewSet, self).get_queryset()

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include user into results whether or not they are public
                queryset = queryset.filter(Q(public=True) | Q(pk=self.request.user.summoner.pk))
            else:
                queryset = queryset.filter(public=True)

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('monsterinstance_set', 'runeinstance_set')  #TODO add other related items here.

        return queryset


class MonsterInstanceViewSet(viewsets.ModelViewSet):
    queryset = MonsterInstance.objects.all().select_related('owner', 'owner__user').prefetch_related('runeinstance_set')
    serializer_class = MonsterInstanceSerializer
    pagination_class = ProfileItemPagination
    # permission_classes = [IsStaffOrOwner]


class RuneInstanceViewSet(viewsets.ModelViewSet):
    queryset = RuneInstance.objects.all().select_related('owner', 'owner__user').prefetch_related('assigned_to__monster')
    serializer_class = RuneInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsStaffOrOwner]
