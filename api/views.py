from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework import viewsets, renderers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bestiary.models import Monster, Skill, LeaderSkill, SkillEffect, Source
from .serializers import MonsterSerializer, MonsterSummarySerializer, MonsterSkillSerializer, \
    MonsterLeaderSkillSerializer, MonsterSkillEffectSerializer, MonsterSourceSerializer


# Pagination classes
class PersonalCollectionSetPagination(PageNumberPagination):
    page_size = 1000


class BestiarySetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# Django REST framework views
class MonsterViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'element', 'archetype', 'base_stars', 'natural_stars', 'obtainable', 'is_awakened', 'com2us_id', 'family_id', 'homunculus')

    def get_serializer_class(self):
        com2us_id = self.request.GET.get('com2us_id', '')
        if self.action == 'list' and len(com2us_id) not in [5, 7]:
            # Return a summary view if no filters are applied
            return MonsterSummarySerializer
        else:
            return MonsterSerializer


class MonsterSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)
    serializer_class = MonsterSkillSerializer
    pagination_class = BestiarySetPagination

    def retrieve(self, request, *args, **kwargs):
        response = super(MonsterSkillViewSet, self).retrieve(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            response = Response({'skill': response.data}, template_name='api/monster_skills/popover.html')

        return response


class MonsterLeaderSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaderSkill.objects.all()
    serializer_class = MonsterLeaderSkillSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillEffectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkillEffect.objects.all()
    serializer_class = MonsterSkillEffectSerializer
    pagination_class = BestiarySetPagination


class MonsterSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = MonsterSourceSerializer
    pagination_class = BestiarySetPagination


@cache_page(60 * 15)
def bestary_stat_charts(request, pk):
    chart_template = {
        'chart': {
            'type': 'line'
        },
        'title': {
            'text': 'Stat Growth By Level'
        },
        'xAxis': {
            'tickInterval': 5,
            'showFirstLabel': True
        },
        'yAxis': [
            {
                'title': {
                    'text': 'HP'
                },
                'id': 'hp',
                'min': 0,
                'opposite': True,
                'endOnTick': False,
            },
            {
                'title': {
                    'text': 'ATK DEF'
                },
                'id': 'atkdef',
                'min': 0,
                'endOnTick': False,
            }
        ],
        'series': None
    }

    monster = Monster.objects.get(pk=pk)

    data_series = []

    for grade in range(monster.natural_stars, 7):
        data_series.append({
            'name': 'HP ' + str(grade) + '*',
            'data': [monster.actual_hp(grade, level) for level in range(1, monster.max_level_from_stars(grade) + 1)],
            'pointStart': 1,
            'visible': True if grade == 6 else False,
            'yAxis': 'hp',
        })
        data_series.append({
            'name': 'ATK ' + str(grade) + '*',
            'data': [monster.actual_attack(grade, level) for level in range(1, monster.max_level_from_stars(grade) + 1)],
            'pointStart': 1,
            'visible': True if grade == 6 else False,
            'yAxis': 'atkdef',
        })
        data_series.append({
            'name': 'DEF ' + str(grade) + '*',
            'data': [monster.actual_defense(grade, level) for level in range(1, monster.max_level_from_stars(grade) + 1)],
            'pointStart': 1,
            'visible': True if grade == 6 else False,
            'yAxis': 'atkdef',
        })

    if data_series:
        # Determine max values for Y axis
        max_stat_value = round(max(
            monster.max_lvl_hp / 15,
            monster.max_lvl_attack,
            monster.max_lvl_defense,
        ))

        chart_template['series'] = data_series
        chart_template['yAxis'][0]['max'] = max_stat_value * 15
        chart_template['yAxis'][1]['max'] = max_stat_value

        return JsonResponse(chart_template, safe=False)
    else:
        return JsonResponse({})
