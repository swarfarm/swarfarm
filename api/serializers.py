from rest_framework import serializers

from herders.models import Monster, MonsterSkill, MonsterLeaderSkill, MonsterSkillEffect, MonsterSource, \
    Summoner, MonsterInstance, RuneInstance, TeamGroup, Team


# Read-only monster database stuff.
class MonsterSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterSource
        exclude = ('icon_filename', 'meta_order')


class MonsterSkillEffectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterSkillEffect
        exclude = ('icon_filename',)


class MonsterSkillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterSkill
        exclude = ('icon_filename',)


class MonsterLeaderSkillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterLeaderSkill


class MonsterSerializer(serializers.HyperlinkedModelSerializer):
    skills = MonsterSkillSerializer(many=True, read_only=True)
    source = MonsterSourceSerializer(many=True, read_only=True)

    class Meta:
        model = Monster
        exclude = ('image_filename',)


# Individual collection stuff
class SummonerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Summoner
        fields = ('id', 'summoner_name', 'global_server',)


class MonsterInstanceSerializer(serializers.HyperlinkedModelSerializer):
    monster = MonsterSerializer(read_only=True)

    class Meta:
        model = MonsterInstance
        fields = (
            'pk', 'monster', 'stars', 'level',
            'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes',
            'hp', 'attack', 'defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
        )
        depth = 1


class RuneInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RuneInstance


class TeamGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TeamGroup


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
