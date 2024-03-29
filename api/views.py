from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework import viewsets, renderers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bestiary.models import Monster, Skill, LeaderSkill, SkillEffect, Source
from herders.models import RuneCraftInstance, MonsterInstance, RuneInstance, TeamGroup, Team, Summoner, ArtifactInstance
from .serializers import MonsterSerializer, MonsterSummarySerializer, MonsterSkillSerializer, \
    MonsterLeaderSkillSerializer, MonsterSkillEffectSerializer, MonsterSourceSerializer, MonsterInstanceSerializer, \
    RuneInstanceSerializer, TeamGroupSerializer, TeamSerializer, ArtifactInstanceSerializer


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


class MonsterInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterInstance.objects.none()
    serializer_class = MonsterInstanceSerializer
    pagination_class = PersonalCollectionSetPagination
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def get_queryset(self):
        # We do not want to allow retrieving all instances
        instance_id = self.kwargs.get('pk', None)

        if instance_id:
            return MonsterInstance.objects.filter(pk=instance_id)
        else:
            return MonsterInstance.objects.none()

    def retrieve(self, request, *args, **kwargs):
        response = super(MonsterInstanceViewSet, self).retrieve(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            return Response({'instance': response.data}, template_name='api/monster_instance/popover.html')
        return response


class RuneInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuneInstance.objects.none()
    serializer_class = RuneInstanceSerializer
    pagination_class = PersonalCollectionSetPagination
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def get_queryset(self):
        # We do not want to allow retrieving all instances
        instance_id = self.kwargs.get('pk', None)

        if instance_id:
            return RuneInstance.objects.filter(pk=instance_id)
        else:
            return RuneInstance.objects.none()

    def retrieve(self, request, *args, **kwargs):
        response = super(RuneInstanceViewSet, self).retrieve(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            return Response({'rune': response.data, 'rta_view': request.GET.get('rune-rta', 'false') == 'true'}, template_name='api/rune_instance/popover.html')
        return response


class ArtifactInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArtifactInstance.objects.none()
    serializer_class = ArtifactInstanceSerializer
    pagination_class = PersonalCollectionSetPagination
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def get_queryset(self):
        # We do not want to allow retrieving all instances
        instance_id = self.kwargs.get('pk', None)

        if instance_id:
            return ArtifactInstance.objects.filter(pk=instance_id)
        else:
            return ArtifactInstance.objects.none()

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            return Response({'artifact': response.data, 'rta_view': request.GET.get('artifact-rta', 'false') == 'true'}, template_name='api/artifact_instance/popover.html')
        return response


class TeamGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeamGroup.objects.all()
    serializer_class = TeamGroupSerializer
    pagination_class = PersonalCollectionSetPagination


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    pagination_class = PersonalCollectionSetPagination


# Custom API
def get_rune_stats_by_slot(request, slot):
    valid_stats = {
        stat: RuneInstance.STAT_CHOICES[stat - 1][1]
        for stat in RuneInstance.MAIN_STATS_BY_SLOT[int(slot)]
    }

    if valid_stats:
        return JsonResponse({
            'code': 'success',
            'data': valid_stats,
        })
    else:
        return JsonResponse({
            'code': 'error',
        })


def get_craft_stats_by_type(request, craft_type):
    valid_stats = RuneCraftInstance.get_valid_stats_for_type(int(craft_type))

    if valid_stats:
        return JsonResponse({
            'code': 'success',
            'data': valid_stats,
        })
    else:
        return JsonResponse({
            'code': 'error',
        })


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


def get_user_messages(request):
    from django.contrib.messages import get_messages

    themessages = get_messages(request)
    data = []

    for message in themessages:
        data.append({
            'text': message.message,
            'status': message.level_tag,
        })

    return JsonResponse({'messages': data})


def nightbot_monsters(request, profile_name, monster_name):
    if monster_name == 'null':
        return HttpResponse('Please specify a monster name like this: !monster baretta')
    try:
        summoner = Summoner.objects.get(user__username=profile_name, public=True)
    except Summoner.DoesNotExist:
        return HttpResponse('Error: No profile with the name "' + profile_name + '" found.')
    else:
        # Filter options
        min_stars = int(request.GET.get('min_stars', 0))
        min_level = int(request.GET.get('min_level', 0))
        mons = MonsterInstance.objects.filter(
            monster__name__istartswith=monster_name,
            owner=summoner,
            runeinstance__isnull=False,
            stars__gte=min_stars,
            level__gte=min_level,
        ).distinct()

        if mons.count() == 0:
            if MonsterInstance.objects.filter(monster__name__istartswith=monster_name, owner=summoner, stars__gte=min_stars, level__gte=min_level).count():
                # See if there were any without runes
                return HttpResponse("Currently not runed.")
            else:
                return HttpResponse(summoner.user.username + " doesn't own one or they were filtered out!")
        else:
            nightbot_responses = []

            for mon in mons:
                desc = mon.monster.name + ': ' + mon.default_build.rune_set_summary
                if mon.notes is not None and mon.notes != '':
                    desc += ' - ' + mon.notes

                # get short URL
                long_url = request.build_absolute_uri(reverse('herders:monster_instance_view', kwargs={'profile_name': summoner.user.username, 'instance_id': mon.pk.hex}))
                desc += ' - ' + long_url
                nightbot_responses.append(desc)

            return HttpResponse(' -AND- '.join(nightbot_responses))

