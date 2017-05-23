from rest_framework import serializers

from herders.models import Summoner, Storage, MonsterInstance, RuneInstance


class RuneInstanceSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.HyperlinkedRelatedField(view_name='apiv2:profiles-detail', source='owner.user.username', read_only=True)
    # TODO: Fix owner field so as not to cause a query explosion


    class Meta:
        model = RuneInstance
        fields = [
            'url', 'pk', 'com2us_id', 'assigned_to',
            'type', 'slot', 'stars', 'level', 'quality', 'original_quality', 'value',
            'substat_upgrades_remaining', 'efficiency', 'max_efficiency',
            'main_stat', 'main_stat_value',
            'innate_stat', 'innate_stat_value',
            'substat_1', 'substat_1_value', 'substat_1_craft',
            'substat_2', 'substat_2_value', 'substat_2_craft',
            'substat_3', 'substat_3_value', 'substat_3_craft',
            'substat_4', 'substat_4_value', 'substat_4_craft',
        ]
        extra_kwargs = {
            'url': {'view_name': 'apiv2:rune-instances-detail'},
            'assigned_to': {'view_name': 'apiv2:monster-instances-detail'},
        }


class MonsterInstanceSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.HyperlinkedRelatedField(view_name='apiv2:profiles-detail', source='owner.user.username', read_only=True)
    # TODO: Fix owner field so as not to cause a query explosion
    runes = RuneInstanceSerializer(many=True, read_only=True, source='runeinstance_set')

    class Meta:
        model = MonsterInstance
        fields = [
            'url', 'pk', 'com2us_id', 'created', 'monster',
            'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes', 'runes',
        ]
        extra_kwargs = {
            'url': {'view_name': 'apiv2:monster-instances-detail'},
            'monster': {'view_name': 'apiv2:bestiary/monsters-detail'},
        }


class SummonerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summoner
        fields = ('url', 'username', 'in_game_name', 'server', 'public',)
        extra_kwargs = {
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'apiv2:profiles-detail',
            },
            'in_game_name': {
                'source': 'summoner_name',
                'allow_blank': True,
            },
        }
