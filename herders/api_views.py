from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from herders.models import BuildingInstance, Storage, MonsterInstance, RuneInstance, RuneCraftInstance
from herders.serializers import *
from herders.pagination import *
from herders.permissions import *


class SummonerViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
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


class MonsterInstanceViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = MonsterInstance.objects.all().select_related('owner', 'owner__user').prefetch_related('runeinstance_set')
    serializer_class = MonsterInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(MonsterInstanceViewSet, self).get_queryset()

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class RuneInstanceViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = RuneInstance.objects.all().select_related('owner', 'owner__user').prefetch_related('assigned_to__monster')
    serializer_class = RuneInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(RuneInstanceViewSet, self).get_queryset()

        if not self.request.user.is_superuser:
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class StorageViewSet(NestedViewSetMixin,
                     viewsets.GenericViewSet):
    # TODO: Raise permission denied if viewing private profile and not owner
    queryset = Storage.objects.all().select_related('owner')
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    # TODO: Set this up to work like an endpoint that only has 1 object
    def list(self, request, *args, **kwargs):
        queryset = super(StorageViewSet, self).get_queryset()
        serialized = StorageSerializer(queryset.first())

        return Response(serialized.data)

    def create(self, request):
        pass






class BuildingViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = BuildingInstance.objects.all()
    serializer_class = BuildingInstanceSerializer
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]