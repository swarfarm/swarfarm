from rest_framework import viewsets, filters
from rest_framework_extensions.mixins import NestedViewSetMixin

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
            queryset = queryset.filter(public=True)

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('monsterinstance_set', 'runeinstance_set')  #TODO add other related items here.

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            # Return a summary view
            return SummonerSerializer
        else:
            return SummonerDetailSerializer


class MonsterInstanceViewSet(viewsets.ModelViewSet):
    queryset = MonsterInstance.objects.all()
    serializer_class = MonsterInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsStaffOrOwner]


class RuneInstanceViewSet(viewsets.ModelViewSet):
    queryset = RuneInstance.objects.all()
    serializer_class = RuneInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsStaffOrOwner]