from rest_framework import viewsets

from herders.models import Monster, MonsterSkill, MonsterSkillEffect, MonsterLeaderSkill, MonsterSource
from .serializers import MonsterSerializer, MonsterSkillSerializer, MonsterLeaderSkillSerializer, MonsterSkillEffectSerializer, MonsterSourceSerializer


# Django REST framework views
class MonsterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer


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
