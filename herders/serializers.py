from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from herders.models import Summoner, Storage, MonsterInstance, RuneInstance


class MonsterInstanceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='apiv2:monster-instance-detail')
    monster = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monsters-detail', read_only=True)
    # TODO: Add owner field

    class Meta:
        model = MonsterInstance
        fields = [
            'url', 'pk', 'com2us_id', 'created', 'monster',
            'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes',
        ]


class RuneInstanceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='apiv2:rune-instance-detail')

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


class SummonerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_name = serializers.CharField(source='summoner_name', allow_blank=True)

    class Meta:
        model = Summoner
        fields = ('url', 'username', 'profile_name', 'server', 'public',)
        extra_kwargs = {
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'apiv2:profile-detail',
            },
        }


class SummonerDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_name = serializers.CharField(source='summoner_name', allow_blank=True)
    monsters = MonsterInstanceSerializer(many=True, read_only=True, source='monsterinstance_set')
    runes = RuneInstanceSerializer(many=True, read_only=True, source='runeinstance_set')

    # TODO: Add URLs to other owned resources.

    class Meta:
        model = Summoner
        fields = ['url', 'username', 'profile_name', 'server', 'public', 'monsters', 'runes']
        extra_kwargs = {
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'apiv2:profile-detail',
            },
        }

