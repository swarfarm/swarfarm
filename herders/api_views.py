from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from herders.models import BuildingInstance, Storage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance
from herders.serializers import *
from herders.pagination import *
from herders.permissions import *


class SummonerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summoner.objects.all().select_related('user')
    serializer_class = SummonerSerializer
    pagination_class = SummonerPagination
    permission_classes = [IsSelfOrPublic]
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

        return queryset


class MonsterInstanceViewSet(viewsets.ModelViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = MonsterInstance.objects.all().select_related('owner', 'owner__user').prefetch_related('runeinstance_set')
    serializer_class = MonsterInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(MonsterInstanceViewSet, self).get_queryset()
        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class RuneInstanceViewSet(viewsets.ModelViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = RuneInstance.objects.all().select_related('owner', 'owner__user').prefetch_related('assigned_to__monster')
    serializer_class = RuneInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(RuneInstanceViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class RuneCraftInstanceViewSet(viewsets.ModelViewSet):
    queryset = RuneCraftInstance.objects.all()
    serializer_class = RuneCraftInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(RuneCraftInstanceViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = BuildingInstance.objects.all()
    serializer_class = BuildingInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(BuildingViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class MonsterPieceViewSet(viewsets.ModelViewSet):
    queryset = MonsterPiece.objects.all()
    serializer_class = MonsterPieceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(MonsterPieceViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class TeamGroupViewSet(viewsets.ModelViewSet):
    queryset = TeamGroup.objects.all()
    serializer_class = TeamGroupSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(TeamGroupViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(TeamViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)
        group = self.kwargs.get('group_pk', None)

        if group is not None and summoner_name is not None:
            queryset = queryset.filter(group__owner__user__username=summoner_name, group=group)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset
