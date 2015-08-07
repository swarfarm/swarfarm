from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from herders.models import Monster, MonsterSkill, MonsterSkillEffect, MonsterLeaderSkill, MonsterSource, \
    Summoner, MonsterInstance, RuneInstance, TeamGroup, Team
from .serializers import MonsterSerializer, MonsterSkillSerializer, MonsterLeaderSkillSerializer, MonsterSkillEffectSerializer, MonsterSourceSerializer, \
    SummonerSerializer, MonsterInstanceSerializer, RuneInstanceSerializer, TeamGroupSerializer, TeamSerializer


# Django REST framework views
class MonsterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('element', 'archetype', 'base_stars', 'obtainable', 'is_awakened')
    search_fields = ('base_hp')


class MonsterSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkill.objects.all()
    serializer_class = MonsterSkillSerializer


class MonsterLeaderSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterLeaderSkill.objects.all()
    serializer_class = MonsterLeaderSkillSerializer


class MonsterSkillEffectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkillEffect.objects.all()
    serializer_class = MonsterSkillEffectSerializer


class MonsterSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSource.objects.all()
    serializer_class = MonsterSourceSerializer


class SummonerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summoner.objects.filter(public=True)
    serializer_class = SummonerSerializer


class MonsterInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterInstance.objects.none()
    serializer_class = MonsterInstanceSerializer

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


class TeamGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeamGroup.objects.all()
    serializer_class = TeamGroupSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
