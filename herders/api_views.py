from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

from herders.models import BuildingInstance, Storage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance
from herders.serializers import *
from herders.pagination import *
from herders.permissions import *


class SummonerViewSet(viewsets.ModelViewSet):
    # queryset = Summoner.objects.all().select_related('user')
    queryset = User.objects.all().select_related('summoner')
    pagination_class = PublicListPagination
    permission_classes = [IsSelfOrPublic]
    lookup_field = 'username'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super(SummonerViewSet, self).get_queryset()

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include current user into results whether or not they are public
                queryset = queryset.filter(Q(summoner__public=True) | Q(pk=self.request.user.pk))
            else:
                queryset = queryset.filter(summoner__public=True)

        return queryset

    def get_serializer_class(self):
        profile_name = self.kwargs.get('pk')
        is_authorized = self.request.user.username == profile_name or self.request.user.is_superuser

        if self.action == 'create' or is_authorized:
            return SummonerSerializer
        else:
            return SummonerSummarySerializer


class MonsterInstanceViewSet(viewsets.ModelViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = MonsterInstance.objects.all().select_related('owner', 'owner__user').prefetch_related(
        'runeinstance_set',
        'runeinstance_set__owner',
        'runeinstance_set__owner__user',
    )
    serializer_class = MonsterInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(MonsterInstanceViewSet, self).get_queryset()
        summoner_name = self.kwargs.get('summoner_pk', None)
        summoner = get_object_or_404(Summoner, user__username=summoner_name)

        if summoner_name is not None:
            queryset = queryset.filter(owner=summoner)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class RuneInstanceViewSet(viewsets.ModelViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = RuneInstance.objects.all().select_related(
        'owner',
        'owner__user',
        'assigned_to',
        'assigned_to__monster',
    )

    serializer_class = RuneInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]
    renderer_classes = [JSONRenderer]  # Browseable API causes major query explosion when trying to generate form options.

    def get_queryset(self):
        queryset = super(RuneInstanceViewSet, self).get_queryset()
        summoner_name = self.kwargs.get('summoner_pk', None)
        summoner = get_object_or_404(Summoner, user__username=summoner_name)

        if summoner_name is not None:
            queryset = queryset.filter(owner=summoner)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class RuneCraftInstanceViewSet(viewsets.ModelViewSet):
    queryset = RuneCraftInstance.objects.all().select_related(
        'owner',
        'owner__user',
    )
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
    queryset = BuildingInstance.objects.all().select_related(
        'building',
        'owner',
        'owner__user',
    )
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
    queryset = MonsterPiece.objects.all().select_related(
        'owner',
        'owner__user',
    )
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
    queryset = TeamGroup.objects.all().select_related(
        'owner',
        'owner__user',
    ).prefetch_related(
        'team_set',
    )
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
    queryset = Team.objects.all().select_related('group').prefetch_related('leader', 'roster')
    serializer_class = TeamSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]
    renderer_classes = [JSONRenderer]  # Browseable API causes major query explosion when trying to generate form options.

    def get_queryset(self):
        queryset = super(TeamViewSet, self).get_queryset()

        summoner_name = self.kwargs.get('summoner_pk', None)

        if summoner_name is not None:
            queryset = queryset.filter(group__owner__user__username=summoner_name)

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(group__owner__public=True) | Q(group__owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(group__owner__public=True)

        return queryset
