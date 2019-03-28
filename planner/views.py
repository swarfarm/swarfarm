from django.db import transaction
from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from bestiary.models import Level
from herders.models import Summoner
from herders.permissions import IsOwner
from . import models, serializers, services


class Pagination(pagination.PageNumberPagination):
    page_size = 10


class OptimizeTeamViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OptimizeTeamSerializer
    # use pagination to work around issues with `list` views
    pagination_class = Pagination
    queryset = models.OptimizeTeam.objects.all()
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve']:
            queryset = queryset.prefetch_related(
                'dungeon', 'monsters', 'monsters__monster'
            )
        return queryset.order_by(
            'dungeon__name', 'name'
        )

    def list(self, request, *args, **kwargs):
        if self.request.accepted_media_type == 'text/html':
            # Avoid heavy lifting to return template
            return Response(template_name='planner/teams.html')
        else:
            return super(OptimizeTeamViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if self.request.accepted_media_type == 'text/html':
            # Avoid heavy lifting to return template
            return Response(template_name='planner/team.html')
        else:
            return super(OptimizeTeamViewSet, self).retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def composite(self, request, *args, **kwargs):
        status_code = 400
        errors = {}
        if request.data['name'] is None:
            errors['name'] = 'Value is required'
        if request.data['teams'] is None:
            errors['teams'] = 'Value is required'
        if models.OptimizeTeam.objects.filter(name=request.data['name']).exists():
            status_code = 409
            errors['name'] = 'Object with name already exists'
        if errors:
            return Response(status=status_code, data=errors)
        # passes validation; create object
        with transaction.atomic():
            composite = services.make_composite(
                owner=Summoner.objects.get(user=request.user),
                name=request.data['name'],
                pks=request.data['teams']
            )
            services.eliminate_redundant_constraints(composite)
        # TODO: CREATED w/ URL
        return Response("created")


class DungeonViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DungeonSerializer
    # use pagination to work around issues with `list` views
    pagination_class = Pagination
    queryset = Level.objects.all()


class RosterViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SummonerRosterSerializer
    # use pagination to work around issues with `list` views
    pagination_class = Pagination
    queryset = Summoner.objects.all().prefetch_related('monsterinstance_set', 'monsterinstance_set__monster')
    lookup_field = 'user'
    lookup_url_kwarg = 'pk'
