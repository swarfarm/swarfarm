from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bestiary import api_filters, models, pagination, serializers


# Django REST framework views
class MonsterViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Monster.objects.all().select_related('leader_skill').prefetch_related(
        'skills',
        'skills__effect',
        'homunculusskill_set',
        'source',
        'monstercraftcost_set',
        'monstercraftcost_set__item',
    ).order_by('pk')
    serializer_class = serializers.MonsterSerializer
    pagination_class = pagination.BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = api_filters.MonsterFilter
    ordering_fields = (
        'com2us_id',
        'family_id',
        'name',
        'element',
        'archetype',
        'base_stars',
        'natural_stars',
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
    queryset = models.Skill.objects.all().prefetch_related(
        'scaling_stats',
        'monster_set',
        'skilleffectdetail_set',
        'skilleffectdetail_set__effect',
    ).order_by('pk')
    serializer_class = serializers.SkillSerializer
    pagination_class = pagination.BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = api_filters.SkillFilter
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
    queryset = models.LeaderSkill.objects.all().order_by('pk')
    serializer_class = serializers.LeaderSkillSerializer
    pagination_class = pagination.BestiarySetPagination
    # TODO: Add filters


class MonsterSkillEffectViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.SkillEffect.objects.all().order_by('pk')
    serializer_class = serializers.SkillEffectSerializer
    pagination_class = pagination.BestiarySetPagination


class MonsterSourceViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Source.objects.all().order_by('pk')
    serializer_class = serializers.SourceSerializer
    pagination_class = pagination.BestiarySetPagination


class HomunculusSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.HomunculusSkill.objects.all().order_by('pk').prefetch_related(
        'skill',
        'skill__monster_set',
        'skill__skilleffectdetail_set',
        'skill__skilleffectdetail_set__effect',
        'homunculusskillcraftcost_set',
        'homunculusskillcraftcost_set__item',
        'prerequisites',
        'monsters',
    )
    serializer_class = serializers.HomunculusSkillSerializer
    pagination_class = pagination.BestiarySetPagination


class GameItemViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.GameItem.objects.all()
    serializer_class = serializers.GameItemSerializer
    pagination_class = pagination.BestiarySetPagination


class FusionViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Fusion.objects.all().prefetch_related(
        'ingredients',
    ).order_by('pk')
    serializer_class = serializers.FusionSerializer
    pagination_class = pagination.BestiarySetPagination


class BuildingViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Building.objects.all().order_by('pk')
    serializer_class = serializers.BuildingSerializer
    pagination_class = pagination.BestiarySetPagination


class DungeonViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Dungeon.objects.all().order_by('pk').prefetch_related('level_set')
    serializer_class = serializers.DungeonSerializer
    pagination_class = pagination.BestiarySetPagination


class LevelViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Level.objects.all().order_by('pk')
    serializer_class = serializers.LevelSerializer
    pagination_class = pagination.BestiarySetPagination