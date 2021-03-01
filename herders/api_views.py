from celery.result import AsyncResult
from django.core.mail import mail_admins
from django.db.models import Q
from django.db.models.signals import post_save
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, parsers, versioning
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from herders.api_filters import ArtifactInstanceFilter, SummonerFilter, MonsterInstanceFilter, RuneInstanceFilter, TeamFilter
from herders.pagination import *
from herders.permissions import *
from herders.serializers import *
from herders.profile_parser import validate_sw_json, default_import_options
from herders.sync_commands import accepted_api_params, active_log_commands
from herders.tasks import com2us_data_import
from herders.models import Summoner, MaterialStorage, MonsterShrineStorage, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance, BuildingInstance, ArtifactCraftInstance, ArtifactInstance
from herders.signals import update_profile_date

from data_log.models import FullLog
from data_log.views import InvalidLogException

import json


class SummonerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('summoner').order_by('pk')
    pagination_class = PublicListPagination
    permission_classes = [IsSelfOrPublic]
    throttle_scope = 'registration'
    lookup_field = 'username'
    lookup_url_kwarg = 'pk'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SummonerFilter

    def get_queryset(self):
        queryset = super(SummonerViewSet, self).get_queryset()

        if not self.request.user.is_superuser and self.action == 'list':
            if self.request.user.is_authenticated:
                # Include current user into results whether or not they are public
                queryset = queryset.filter(
                    Q(summoner__public=True) | Q(pk=self.request.user.pk))
            else:
                queryset = queryset.filter(summoner__public=True)

        return queryset

    def get_serializer_class(self):
        profile_name = self.kwargs.get('pk')
        is_authorized = self.request.user.username == profile_name

        if (is_authorized or self.request.user.is_superuser) or self.action == 'create':
            return FullUserSerializer
        else:
            return SummonerSerializer


class GlobalMonsterInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterInstance.objects.filter(owner__public=True).select_related(
        'monster',
        'owner__user',
    ).prefetch_related(
        'runeinstance_set',
        'runeinstance_set__owner__user',
    ).order_by()
    serializer_class = MonsterInstanceSerializer
    permission_classes = [AllowAny]
    pagination_class = PublicListPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MonsterInstanceFilter


class GlobalRuneInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuneInstance.objects.filter(owner__public=True).select_related(
        'owner',
        'owner__user',
        'assigned_to',
    ).order_by()
    serializer_class = RuneInstanceSerializer
    permission_classes = [AllowAny]
    pagination_class = PublicListPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RuneInstanceFilter


class ProfileItemMixin(viewsets.GenericViewSet):
    pagination_class = ProfileItemPagination
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super(ProfileItemMixin, self).get_queryset()
        username = self.kwargs.get('user_pk')

        if username is None:
            return queryset.none()

        queryset = queryset.filter(owner__user__username=username)

        if not self.request.user.is_superuser and self.action == 'list':
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(owner__public=True) | Q(
                    owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(owner__public=True)

        return queryset


class StorageViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = MaterialStorage.objects.all().select_related(
        'owner', 'owner__user', 'item')
    serializer_class = MaterialStorageSerializer


class MonsterShrineStorageViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = MonsterShrineStorage.objects.all().select_related('owner',
                                                                 'owner__user', 'item')
    serializer_class = MonsterShrineStorageSerializer


class RuneBuildViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = RuneBuild.objects.all().select_related(
        'owner',
        'owner__user'
    ).prefetch_related(
        'runes',
        'runes__owner',
        'runes__owner__user'
    ).order_by()
    serializer_class = RuneBuildSerializer


class MonsterInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = MonsterInstance.objects.all().select_related(
        'monster',
        'default_build',
        'rta_build'
    ).prefetch_related(
        'default_build__runes',
        'rta_build__runes',
        'runeinstance_set',
        'runeinstance_set__owner__user',
    )
    serializer_class = MonsterInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = MonsterInstanceFilter
    ordering_fields = (
        'stars',
        'level',
        'created',
        'base_attack',
        'rune_attack',
        'base_defense',
        'rune_defense',
        'base_speed',
        'rune_speed',
        'base_crit_rate',
        'rune_crit_rate',
        'base_crit_damage',
        'rune_crit_damage',
        'base_resistance',
        'rune_resistance',
        'base_accuracy',
        'rune_accuracy',
        'avg_efficiency',
        'fodder',
        'in_storage',
        'ignore_for_fusion',
        'priority',
        'monster__com2us_id',
        'monster__family_id',
        'monster__name',
        'monster__element',
        'monster__archetype',
        'monster__base_stars',
        'monster__natural_stars',
        'monster__can_awaken',
        'monster__is_awakened',
        'monster__base_hp',
        'monster__base_attack',
        'monster__base_defense',
        'monster__speed',
        'monster__crit_rate',
        'monster__crit_damage',
        'monster__resistance',
        'monster__accuracy',
        'monster__raw_hp',
        'monster__raw_attack',
        'monster__raw_defense',
        'monster__max_lvl_hp',
        'monster__max_lvl_attack',
        'monster__max_lvl_defense',
    )


class RuneInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = RuneInstance.objects.all().select_related(
        'owner__user',
        'assigned_to',
    )
    serializer_class = RuneInstanceSerializer
    # renderer_classes = [JSONRenderer]  # Browseable API causes major query explosion when trying to generate form options.
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = RuneInstanceFilter
    ordering_fields = (
        'type',
        'level',
        'stars',
        'slot',
        'quality',
        'original_quality',
        'assigned_to',
        'main_stat',
        'innate_stat',
        'marked_for_sale',
    )


class ArtifactInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = ArtifactInstance.objects.all().select_related(
        'owner__user',
        'assigned_to',
    )
    serializer_class = ArtifactInstanceSerializer
    # renderer_classes = [JSONRenderer]  # Browseable API causes major query explosion when trying to generate form options.
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = ArtifactInstanceFilter
    ordering_fields = (
        'level',
        'stars',
        'slot',
        'quality',
        'original_quality',
        'assigned_to',
        'main_stat',
    )


class RuneCraftInstanceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = RuneCraftInstance.objects.all().select_related(
        'owner',
        'owner__user',
    )
    serializer_class = RuneCraftInstanceSerializer


class BuildingViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = BuildingInstance.objects.all().select_related(
        'building',
        'owner',
        'owner__user',
    )
    serializer_class = BuildingInstanceSerializer


class MonsterPieceViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = MonsterPiece.objects.all().select_related(
        'owner',
        'owner__user',
    )
    serializer_class = MonsterPieceSerializer


class TeamGroupViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = TeamGroup.objects.all().select_related(
        'owner',
        'owner__user',
    ).prefetch_related(
        'team_set',
    )
    serializer_class = TeamGroupSerializer


class TeamViewSet(ProfileItemMixin, viewsets.ModelViewSet):
    queryset = Team.objects.all().select_related('group', 'leader').prefetch_related(
        'leader__runeinstance_set', 'roster', 'roster__runeinstance_set')
    serializer_class = TeamSerializer
    # Browseable API causes major query explosion when trying to generate form options.
    renderer_classes = [JSONRenderer]
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = TeamFilter

    def get_queryset(self):
        # Team objects do not have an owner field, so we must go through the group owner for filtering
        queryset = super(ProfileItemMixin, self).get_queryset()
        summoner_name = self.kwargs.get('user_pk')

        if summoner_name is not None:
            queryset = queryset.filter(
                group__owner__user__username=summoner_name)

        if not self.request.user.is_superuser and self.action == 'list':
            if self.request.user.is_authenticated:
                # Include active user into results whether or not they are public so they can view themselves
                queryset = queryset.filter(Q(group__owner__public=True) | Q(
                    group__owner=self.request.user.summoner))
            else:
                queryset = queryset.filter(group__owner__public=True)

        return queryset


class ProfileJsonUpload(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        errors = []
        validation_failures = []

        schema_errors, validation_errors = validate_sw_json(
            request.data, request.user.summoner)

        if schema_errors:
            errors.append(schema_errors)

        if validation_errors:
            validation_failures = "Uploaded data does not match previously imported data. To override, set import preferences to ignore validation errors and import again."

        import_options = request.user.summoner.preferences.get(
            'import_options', default_import_options)

        if not errors and (not validation_failures or import_options['ignore_validation_errors']):
            # Queue the import
            task = com2us_data_import.delay(
                request.data, request.user.summoner.pk, import_options)
            return Response({'job_id': task.task_id})

        elif validation_failures:
            return Response({'validation_error': validation_failures}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'error': errors}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, user_pk=None, pk=None):
        task = AsyncResult(pk)

        if task:
            try:
                return Response({
                    'status': task.status,
                })
            except:
                return Response({
                    'status': 'error',
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SyncData(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    # Ignore default of namespaced based versioning and use default version defined in settings
    versioning_class = versioning.QueryParameterVersioning
    parser_classes = (parsers.JSONParser, parsers.FormParser)

    def create(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Unauthorized, make sure that API Key is correct"}, status=status.HTTP_401_UNAUTHORIZED)

        log_data = request.data.get('data')

        if request.content_type == 'application/x-www-form-urlencoded':
            # log_data will be a string, needs to be parsed as json
            log_data = json.loads(log_data)

        try:
            api_command = log_data['request']['command'] if log_data.get('request') and log_data['request'].get('command') else log_data['response']['command']
            # HubUserLogin is a special case, it doesn't store `wizard_id` in request since it needs to fetch it first
            wizard_id = log_data['request']['wizard_id'] if api_command != "HubUserLogin" else log_data['response']['wizard_info']['wizard_id']
        except (KeyError, TypeError):
            raise InvalidLogException(detail='Invalid log data format')

        if api_command not in active_log_commands:
            raise InvalidLogException('Unsupported game command')

        summoner = request.user.summoner

        if summoner.com2us_id != wizard_id:
            return Response({'detail': "Uploaded data does not match previously imported data. Make sure you are trying to synchronize correct account"}, status=status.HTTP_409_CONFLICT)

        # Validate log data format
        if not active_log_commands[api_command].validate(log_data):
            FullLog.parse(summoner, log_data)
            raise InvalidLogException(detail='Log data failed validation')

        # Disconnect summoner profile last update post-save signal to avoid mass spamming updates
        post_save.disconnect(update_profile_date, sender=MonsterInstance)
        post_save.disconnect(update_profile_date, sender=MonsterPiece)
        post_save.disconnect(update_profile_date, sender=RuneInstance)
        post_save.disconnect(update_profile_date, sender=RuneCraftInstance)
        post_save.disconnect(update_profile_date, sender=ArtifactInstance)
        post_save.disconnect(update_profile_date, sender=ArtifactCraftInstance)
        post_save.disconnect(update_profile_date, sender=MaterialStorage)
        post_save.disconnect(update_profile_date, sender=MonsterShrineStorage)
        post_save.disconnect(update_profile_date, sender=BuildingInstance)

        # Parse the log
        try:
            sync_conflict = active_log_commands[api_command].parse(
                summoner,
                log_data
            )
        except Exception as e:
            mail_admins('Log server error', f'Request body:\n\n{log_data}')
            raise e

        if sync_conflict:
            return Response({"detail": "Data conflict, synchronization failed. Try logging in again to synchronize your entire profile with SWARFARM"}, status=status.HTTP_409_CONFLICT)

        # update summoner profile last update date
        summoner.save()
        response = {'detail': 'Log OK'}

        # Check if accepted API params version matches the active version
        if log_data.get('__version') != accepted_api_params['__version']:
            response['reinit'] = True

        return Response(response)


class SyncAcceptedCommands(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    # Ignore default of namespaced based versioning and use default version defined in settings
    versioning_class = versioning.QueryParameterVersioning
    renderer_classes = (JSONRenderer, )

    def list(self, request):
        return Response(accepted_api_params)
