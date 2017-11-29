from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer

from herders.models import BuildingInstance, Storage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance
from herders.serializers import *
from herders.pagination import *
from herders.permissions import *
from herders.api_filters import SummonerFilter, MonsterInstanceFilter, RuneInstanceFilter


class SummonerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('summoner').order_by('pk')
    pagination_class = PublicListPagination
    permission_classes = [IsSelfOrPublic]
    throttle_scope = 'registration'
    lookup_field = 'username'
    lookup_url_kwarg = 'pk'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SummonerFilter

    def get_queryset(self):
        queryset = super(SummonerViewSet, self).get_queryset()

        if not self.request.user.is_superuser and self.action == 'list':
            if self.request.user.is_authenticated:
                # Include current user into results whether or not they are public
                queryset = queryset.filter(Q(summoner__public=True) | Q(pk=self.request.user.pk))
            else:
                queryset = queryset.filter(summoner__public=True)

        return queryset

    def get_serializer_class(self):
        profile_name = self.kwargs.get('pk')
        is_authorized = self.request.user.username == profile_name

        if (is_authorized or self.request.user.is_superuser) or self.action == 'create':
            return FullUserSerializer
        else:
            return SummonerSerializer


class GlobalMonsterInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterInstance.objects.filter(owner__public=True).select_related(
        'monster',
        'owner__user',
    ).prefetch_related(
        'runeinstance_set',
        'runeinstance_set__owner__user',
    ).order_by()
    serializer_class = MonsterInstanceSerializer
    permission_classes = [AllowAny]
    pagination_class = PublicListPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MonsterInstanceFilter


class GlobalRuneInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuneInstance.objects.filter(owner__public=True).select_related(
        'owner',
        'owner__user',
        'assigned_to',
    ).order_by()
    serializer_class = RuneInstanceSerializer
    permission_classes = [AllowAny]
    pagination_class = PublicListPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RuneInstanceFilter


class ProfileItemMixin(viewsets.GenericViewSet):
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(ProfileItemMixin, self).get_queryset()
        username = self.kwargs.get('user_pk')

        if username is None:
            raise Http404()

        queryset = queryset.filter(owner__user__username=username)

        if not self.request.user.is_superuser and self.action == 'list':
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class StorageViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = Storage.objects.all().select_related('owner', 'owner__user')
    serializer_class = StorageSerializer

    def get_object(self):
        username = self.kwargs.get('user_pk')
        filter_kwargs = {'owner__user__username': username}
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **filter_kwargs)

        return obj


class MonsterInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = MonsterInstance.objects.all().select_related('owner', 'owner__user').prefetch_related(
        'runeinstance_set',
        'runeinstance_set__owner__user',
    )
    serializer_class = MonsterInstanceSerializer


class RuneInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = RuneInstance.objects.all().select_related(
        'owner__user',
        'assigned_to',
    )
    serializer_class = RuneInstanceSerializer
    # renderer_classes = [JSONRenderer]  # Browseable API causes major query explosion when trying to generate form options.


class RuneCraftInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = RuneCraftInstance.objects.all().select_related(
        'owner',
        'owner__user',
    )
    serializer_class = RuneCraftInstanceSerializer


class BuildingViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = BuildingInstance.objects.all().select_related(
        'building',
        'owner',
        'owner__user',
    )
    serializer_class = BuildingInstanceSerializer


class MonsterPieceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = MonsterPiece.objects.all().select_related(
        'owner',
        'owner__user',
    )
    serializer_class = MonsterPieceSerializer


class TeamGroupViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = TeamGroup.objects.all().select_related(
        'owner',
        'owner__user',
    ).prefetch_related(
        'team_set',
    )
    serializer_class = TeamGroupSerializer


class TeamViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = Team.objects.all().select_related('group').prefetch_related('leader', 'roster')
    serializer_class = TeamSerializer
    renderer_classes = [JSONRenderer]  # Browseable API causes major query explosion when trying to generate form options.

    def get_queryset(self):
        # Team objects do not have an owner field, so we must go through the group owner for filtering
        queryset = super(ProfileItemMixin, self).get_queryset()
        summoner_name = self.kwargs.get('user_pk')

        if summoner_name is not None:
            queryset = queryset.filter(group__owner__user__username=summoner_name)

        if not self.request.user.is_superuser and self.action == 'list':
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(group__owner__public=True) | Q(group__owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(group__owner__public=True)

        return queryset
