from rest_framework import serializers

from herders.models import Monster, MonsterSkill, MonsterLeaderSkill, MonsterSkillEffect, MonsterSource


class MonsterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Monster


class MonsterSkillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterSkill


class MonsterLeaderSkillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterLeaderSkill


class MonsterSkillEffectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterSkillEffect


class MonsterSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonsterSource
