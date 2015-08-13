from rest_framework import serializers

from herders.models import Monster, MonsterSkill, MonsterLeaderSkill, MonsterSkillEffect, MonsterSource, \
    Summoner, MonsterInstance, RuneInstance, TeamGroup, Team


# Read-only monster database stuff.
class MonsterSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonsterSource
        exclude = 'meta_order'


class MonsterSkillEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonsterSkillEffect
        fields = ('pk', 'name', 'is_buff', 'description', 'icon_filename')


class MonsterSkillSerializer(serializers.HyperlinkedModelSerializer):
    skill_effect = MonsterSkillEffectSerializer(many=True, read_only=True)

    class Meta:
        model = MonsterSkill


class MonsterLeaderSkillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterLeaderSkill


# Small serializer for necessary info for awakens_from/to on main MonsterSerializer
class AwakensMonsterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Monster
        fields = ('pk', 'name', 'image_filename')


class MonsterSerializer(serializers.HyperlinkedModelSerializer):
    awakens_from = AwakensMonsterSerializer(read_only=True)
    awakens_to = AwakensMonsterSerializer(read_only=True)
    source = MonsterSourceSerializer(many=True, read_only=True)
    skills = MonsterSkillSerializer(many=True, read_only=True)
    # all_skill_effects = MonsterSkillEffectSerializer(many=True, read_only=True)

    class Meta:
        model = Monster
        fields = (
            'pk', 'name', 'image_filename', 'element', 'archetype', 'base_stars',
            'obtainable', 'can_awaken', 'is_awakened', 'awaken_bonus',
            'skills', 'leader_skill',
            'base_hp', 'base_attack', 'base_defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
            'awakens_from', 'awakens_to',
            'awaken_ele_mats_low', 'awaken_ele_mats_mid', 'awaken_ele_mats_high',
            'awaken_magic_mats_low', 'awaken_magic_mats_mid', 'awaken_magic_mats_high',
            'source', 'fusion_food'
        )


# Limited fields for displaying list view sort of display.
class MonsterSummarySerializer(serializers.HyperlinkedModelSerializer):
    awakens_from = AwakensMonsterSerializer(read_only=True)
    awakens_to = AwakensMonsterSerializer(read_only=True)
    all_skill_effects = MonsterSkillEffectSerializer(many=True, read_only=True)

    class Meta:
        model = Monster
        fields = (
            'pk', 'name', 'image_filename', 'element', 'archetype', 'base_stars',
            'obtainable', 'can_awaken', 'is_awakened', 'awakens_from', 'awakens_to', 'get_awakening_materials',
            'fusion_food', 'all_skill_effects',
        )


# Individual collection stuff
class SummonerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Summoner
        fields = ('id', 'summoner_name', 'global_server',)


class MonsterInstanceSerializer(serializers.ModelSerializer):
    monster = MonsterSerializer(read_only=True)

    class Meta:
        model = MonsterInstance
        fields = (
            'pk', 'monster', 'stars', 'level',
            'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes',
            'hp', 'attack', 'defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
            'team_leader', 'team_set', 'runeinstance_set'
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
