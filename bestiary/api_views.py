from rest_framework import viewsets, filters, renderers
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bestiary.serializers import *
from bestiary.pagination import *
from bestiary.filters import MonsterFilter


# Django REST framework views
class MonsterViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all().prefetch_related('skills', 'homunculusskill_set', 'source')
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = MonsterSerializer
    pagination_class = BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MonsterFilter


class MonsterSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = SkillSerializer
    pagination_class = BestiarySetPagination


class MonsterLeaderSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = LeaderSkill.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = LeaderSkillSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillEffectViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Effect.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = SkillEffectSerializer
    pagination_class = BestiarySetPagination


class MonsterSourceViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = SourceSerializer
    pagination_class = BestiarySetPagination


class HomunculusSkillViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = HomunculusSkill.objects.all().order_by('pk')
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = HomunculusSkillSerializer
    pagination_class = BestiarySetPagination


class CraftMaterialViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CraftMaterial.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    serializer_class = CraftMaterialSerializer
    pagination_class = BestiarySetPagination
