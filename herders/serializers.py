from rest_framework import serializers
from rest_framework_nested.relations import NestedHyperlinkedIdentityField, NestedHyperlinkedRelatedField

from herders.models import Summoner, Storage, BuildingInstance, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance, TeamGroup, Team


class RuneInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/runes-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )
    # owner = serializers.HyperlinkedRelatedField(view_name='apiv2:profiles-detail', source='owner.user.username', read_only=True)
    # TODO: Fix owner field so as not to cause a query explosion

    class Meta:
        model = RuneInstance
        fields = [
            'pk', 'url', 'com2us_id', 'assigned_to',
            'type', 'slot', 'stars', 'level', 'quality', 'original_quality', 'value',
            'substat_upgrades_remaining', 'efficiency', 'max_efficiency',
            'main_stat', 'main_stat_value',
            'innate_stat', 'innate_stat_value',
            'substat_1', 'substat_1_value', 'substat_1_craft',
            'substat_2', 'substat_2_value', 'substat_2_craft',
            'substat_3', 'substat_3_value', 'substat_3_craft',
            'substat_4', 'substat_4_value', 'substat_4_craft',
        ]


class RuneCraftInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/rune-crafts-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    class Meta:
        model = RuneCraftInstance
        fields = ['pk', 'url', 'com2us_id', 'type', 'rune', 'stat', 'quality', 'value']


class MonsterInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/monsters-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )
    # owner = serializers.HyperlinkedRelatedField(view_name='apiv2:profiles-detail', source='owner.user.username', read_only=True)
    # TODO: Fix owner field so as not to cause a query explosion
    runes = RuneInstanceSerializer(many=True, read_only=True, source='runeinstance_set')

    class Meta:
        model = MonsterInstance
        fields = [
            'pk', 'url', 'com2us_id', 'created', 'monster',
            'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes', 'runes',
        ]


class MonsterPieceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/monster-pieces-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    class Meta:
        model = MonsterPiece
        fields = ['url', 'pk', 'monster', 'pieces']


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = [
            'magic_essence', 'fire_essence', 'water_essence', 'wind_essence', 'light_essence', 'dark_essence',
            'wood', 'leather', 'rock', 'ore', 'mithril', 'cloth', 'rune_piece', 'dust',
            'symbol_harmony',  'symbol_transcendance', 'symbol_chaos',
            'crystal_water', 'crystal_fire', 'crystal_wind', 'crystal_light', 'crystal_dark', 'crystal_magic', 'crystal_pure',
        ]


class BuildingInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/buildings-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    class Meta:
        model = BuildingInstance
        fields = ['pk', 'url', 'building', 'level']


class SummonerSerializer(serializers.ModelSerializer):
    in_game_name = serializers.CharField(source='summoner_name', read_only=True)
    storage = StorageSerializer()

    class Meta:
        model = Summoner
        fields = ['url', 'username', 'in_game_name', 'server', 'public', 'storage']
        extra_kwargs = {
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'apiv2:profiles-detail',
            }
        }


class TeamGroupSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/team-groups-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    teams = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True,
        source='team_set',
    )

    class Meta:
        model = TeamGroup
        fields = ['pk', 'url', 'name', 'teams']


class TeamSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='apiv2:profile/teams-detail',
        parent_lookup_kwargs={
            'summoner_pk': 'group__owner__user__username',
            'group_pk': 'group__pk',
        },
    )

    class Meta:
        model = Team
        fields = ['pk', 'url', 'favorite', 'name', 'description', 'leader', 'roster']