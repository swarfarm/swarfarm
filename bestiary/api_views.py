from rest_framework import viewsets, filters
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bestiary.serializers import *
from bestiary.pagination import *
from bestiary.filters import MonsterFilter


# Django REST framework views
class MonsterViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all().select_related('leader_skill').prefetch_related(
        'skills',
        'skills__effect',
        'homunculusskill_set',
        'source',
        'monstercraftcost_set',
        'monstercraftcost_set__craft',
    )
    serializer_class = MonsterSerializer
    pagination_class = BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MonsterFilter


class MonsterSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all().prefetch_related(
        'monster_set',
        'monsterskilleffectdetail_set',
        'monsterskilleffectdetail_set__effect',
    )
    serializer_class = SkillSerializer
    pagination_class = BestiarySetPagination


class MonsterLeaderSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = LeaderSkill.objects.all()
    serializer_class = LeaderSkillSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillEffectViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Effect.objects.all()
    serializer_class = SkillEffectSerializer
    pagination_class = BestiarySetPagination


class MonsterSourceViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    pagination_class = BestiarySetPagination


class HomunculusSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = HomunculusSkill.objects.all().order_by('pk').prefetch_related(
        'skill',
        'skill__monster_set',
        'skill__monsterskilleffectdetail_set',
        'skill__monsterskilleffectdetail_set__effect',
        'homunculusskillcraftcost_set',
        'prerequisites',
    )
    serializer_class = HomunculusSkillSerializer
    pagination_class = BestiarySetPagination


class CraftMaterialViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CraftMaterial.objects.all()
    serializer_class = CraftMaterialSerializer
    pagination_class = BestiarySetPagination


class FusionViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Fusion.objects.all().prefetch_related(
        'ingredients',
    )
    serializer_class = FusionSerializer
    pagination_class = BestiarySetPagination


class BuildingViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    pagination_class = BestiarySetPagination
