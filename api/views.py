from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, filters, renderers
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from urllib2 import Request, urlopen, HTTPError
import json

from bestiary.models import Monster, Skill, LeaderSkill
from herders.models import Summoner, MonsterInstance, RuneInstance, RuneCraftInstance, Team, TeamGroup
from .serializers import *


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
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'element', 'archetype', 'base_stars', 'obtainable', 'is_awakened', 'com2us_id', 'family_id')

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
    queryset = Effect.objects.all()
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
            # print response.data
            return Response({'rune': response.data}, template_name='api/rune_instance/popover.html')
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
    valid_stats = RuneInstance.get_valid_stats_for_slot(int(slot))

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
                'opposite': True,
                'endOnTick': False,
            },
            {
                'title': {
                    'text': 'ATK DEF'
                },
                'id': 'atkdef',
                'endOnTick': False,
            }
        ],
        'series': None
    }

    monster = Monster.objects.get(pk=pk)

    data_series = []

    if monster.is_awakened and monster.awakens_from and monster.base_stars >= 2:
        base_stars = monster.awakens_from.base_stars
    else:
        base_stars = monster.base_stars

    for grade in range(base_stars, 7):
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
        max_stat_value = max(
            monster.max_lvl_hp / 15,
            monster.max_lvl_attack,
            monster.max_lvl_defense,
        )

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


def summoner_monster_view_list(request, profile_name):
    try:
        summoner = Summoner.objects.get(user__username=profile_name, public=True)
    except Summoner.DoesNotExist:
        raise Http404()
    else:
        url_list = []
        monsters = MonsterInstance.objects.filter(owner=summoner)

        for m in monsters:
            url_list.append({
                'monster': str(m),
                'url': request.build_absolute_uri(reverse('herders:monster_instance_view', kwargs={'profile_name': summoner.user.username, 'instance_id': m.pk.hex}))
            })

        return JsonResponse(url_list, safe=False)


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
                desc = mon.monster.name + ': ' + mon.get_rune_set_summary()
                if mon.notes is not None and mon.notes != '':
                    desc += ' - ' + mon.notes

                # get short URL
                long_url = request.build_absolute_uri(reverse('herders:monster_instance_view', kwargs={'profile_name': summoner.user.username, 'instance_id': mon.pk.hex}))
                google_api = 'https://www.googleapis.com/urlshortener/v1/url?key=' + settings.GOOGLE_API_KEY
                data = json.dumps({
                    'longUrl': long_url
                })
                try:
                    req = Request(google_api, data, {'Content-Type': 'application/json'})
                    f = urlopen(req)
                    response = f.read()
                    f.close()
                    response = json.loads(response)
                    short_url = response['id']
                except HTTPError:
                    desc += ' - ' + long_url
                else:
                    desc += ' - ' + short_url

                nightbot_responses.append(desc)

            return HttpResponse(' -AND- '.join(nightbot_responses))

