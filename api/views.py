from rest_framework import viewsets, filters, status, renderers
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from herders.models import *
from .serializers import *


# Pagination classes
class PersonalCollectionSetPagination(PageNumberPagination):
    page_size = 1000


class BestiarySetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000


# Django REST framework views
class MonsterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monster.objects.all()
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    pagination_class = BestiarySetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('element', 'archetype', 'base_stars', 'obtainable', 'is_awakened')

    def get_serializer_class(self):
        if self.action == 'list':
            return MonsterSummarySerializer
        else:
            return MonsterSerializer

    def list(self, request, *args, **kwargs):
        response = super(MonsterViewSet, self).list(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            return Response({'data': response.data['results']}, template_name='api/bestiary/table_rows.html')
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super(MonsterViewSet, self).retrieve(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            return Response({'monster': response.data}, template_name='api/bestiary/detail.html')
        return response


class MonsterSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkill.objects.all()
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)
    serializer_class = MonsterSkillSerializer
    pagination_class = BestiarySetPagination

    def retrieve(self, request, *args, **kwargs):
        response = super(MonsterSkillViewSet, self).retrieve(request, *args, **kwargs)

        if request.accepted_renderer.format == 'html':
            response = Response({'skill': response.data}, template_name='api/monster_skills/popover.html')

        return response


class MonsterLeaderSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterLeaderSkill.objects.all()
    serializer_class = MonsterLeaderSkillSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillEffectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkillEffect.objects.all()
    serializer_class = MonsterSkillEffectSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillScalesWithViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkillScalesWith.objects.all()
    serializer_class = MonsterSkillScalesWithSerializer
    pagination_class = BestiarySetPagination


class MonsterSkillScalesWithDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterSkillScalingStat.objects.all()
    serializer_class = MonsterSkillScalingStatSerializer
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
    from django.http import JsonResponse

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


def get_user_messages(request):
    from django.http import JsonResponse
    from django.contrib.messages import get_messages

    themessages = get_messages(request)
    data = []

    for message in themessages:
        data.append({
            'text': message.message,
            'status': message.level_tag,
        })

    return JsonResponse({'messages': data})
