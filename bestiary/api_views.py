from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bestiary.api_filters import MonsterFilter, SkillFilter
from bestiary.pagination import *
from bestiary.serializers import *


# Django REST framework views
class MonsterViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all().select_related('leader_skill').prefetch_related(
        'skills',
        'skills__effect',
        'homunculusskill_set',
        'source',
        'monstercraftcost_set',
        'monstercraftcost_set__craft',
        'monsterguide_set',
    ).order_by('pk')
    serializer_class = MonsterSerializer
    pagination_class = BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = MonsterFilter
    ordering_fields = (
        'com2us_id',
        'family_id',
        'name',
        'element',
        'archetype',
        'base_stars',
        'can_awaken',
        'is_awakened',
        'base_hp',
        'base_attack',
        'base_defense',
        'speed',
        'crit_rate',
        'crit_damage',
        'resistance',
        'accuracy',
        'raw_hp',
        'raw_attack',
        'raw_defense',
        'max_lvl_hp',
        'max_lvl_attack',
        'max_lvl_defense',
    )


class MonsterSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all().prefetch_related(
        'scaling_stats',
        'monster_set',
        'monsterskilleffectdetail_set',
        'monsterskilleffectdetail_set__effect',
    ).order_by('pk')
    serializer_class = SkillSerializer
    pagination_class = BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = SkillFilter
    ordering_fields = (
        'name',
        'slot',
        'cooltime',
        'hits',
        'aoe',
        'passive',
        'max_level',
    )


class MonsterLeaderSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = LeaderSkill.objects.all().order_by('pk')
    serializer_class = LeaderSkillSerializer
    pagination_class = BestiarySetPagination
    # TODO: Add filters


class MonsterSkillEffectViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Effect.objects.all().order_by('pk')
    serializer_class = SkillEffectSerializer
    pagination_class = BestiarySetPagination


class MonsterSourceViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all().order_by('pk')
    serializer_class = SourceSerializer
    pagination_class = BestiarySetPagination


class HomunculusSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = HomunculusSkill.objects.all().order_by('pk').prefetch_related(
        'skill',
        'skill__monster_set',
        'skill__monsterskilleffectdetail_set',
        'skill__monsterskilleffectdetail_set__effect',
        'homunculusskillcraftcost_set',
        'homunculusskillcraftcost_set__craft',
        'prerequisites',
        'monsters',
    )
    serializer_class = HomunculusSkillSerializer
    pagination_class = BestiarySetPagination


class CraftMaterialViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CraftMaterial.objects.all().order_by('pk')
    serializer_class = CraftMaterialSerializer
    pagination_class = BestiarySetPagination


class FusionViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Fusion.objects.all().prefetch_related(
        'ingredients',
    ).order_by('pk')
    serializer_class = FusionSerializer
    pagination_class = BestiarySetPagination


class BuildingViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Building.objects.all().order_by('pk')
    serializer_class = BuildingSerializer
    pagination_class = BestiarySetPagination
