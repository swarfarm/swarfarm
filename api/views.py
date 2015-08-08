from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from herders.models import Monster, MonsterSkill, MonsterSkillEffect, MonsterLeaderSkill, MonsterSource, \
    Summoner, MonsterInstance, RuneInstance, TeamGroup, Team
from .serializers import MonsterSerializer, MonsterSkillSerializer, MonsterLeaderSkillSerializer, MonsterSkillEffectSerializer, MonsterSourceSerializer, \
    SummonerSerializer, MonsterInstanceSerializer, RuneInstanceSerializer, TeamGroupSerializer, TeamSerializer


# Pagination classes
class PersonalCollectionSetPagination(PageNumberPagination):
    page_size = 1000


class BestiarySetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# Django REST framework views
class MonsterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer
    pagination_class = BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('element', 'archetype', 'base_stars', 'obtainable', 'is_awakened')
    search_fields = ('base_hp')


class MonsterSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkill.objects.all()
    serializer_class = MonsterSkillSerializer
    pagination_class = BestiarySetPagination


class MonsterLeaderSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterLeaderSkill.objects.all()
    serializer_class = MonsterLeaderSkillSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillEffectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkillEffect.objects.all()
    serializer_class = MonsterSkillEffectSerializer
    pagination_class = BestiarySetPagination


class MonsterSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSource.objects.all()
    serializer_class = MonsterSourceSerializer
    pagination_class = BestiarySetPagination


class SummonerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summoner.objects.filter(public=True)
    serializer_class = SummonerSerializer


class MonsterInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterInstance.objects.none()
    serializer_class = MonsterInstanceSerializer
    pagination_class = PersonalCollectionSetPagination

    def get_queryset(self):
        profile_name = self.kwargs.get('profile_name', None)
        instance_id = self.kwargs.get('instance_id', None)

        if profile_name:
            summoner = get_object_or_404(Summoner, user__username=profile_name)
            is_owner = (self.request.user.is_authenticated() and summoner.user == self.request.user)

            if is_owner or summoner.public:
                if instance_id:
                    # Return single monster
                    return get_object_or_404(MonsterInstance, pk=instance_id)
                else:
                    # Return list of monsters owned
                    return MonsterInstance.objects.filter(owner=summoner)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RuneInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuneInstance.objects.all()
    serializer_class = RuneInstanceSerializer
    pagination_class = PersonalCollectionSetPagination


class TeamGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeamGroup.objects.all()
    serializer_class = TeamGroupSerializer
    pagination_class = PersonalCollectionSetPagination


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    pagination_class = PersonalCollectionSetPagination
