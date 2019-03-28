from drf_writable_nested.mixins import GetOrCreateNestedSerializerMixin, RelatedSaveMixin
from rest_framework import serializers
from rest_framework.compat import unicode_to_repr

from bestiary.models import Level
from herders import models as herders
from . import models


class CurrentSummonerDefault(object):
    def set_context(self, serializer_field):
        self.user = serializer_field.context['request'].user

    def __call__(self):
        return self.user.summoner

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class DungeonSerializer(GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name']
        extra_kwargs = {
            'max_slots': {'read_only': True},
            # for matching, need to make explicit (see https://github.com/encode/django-rest-framework/issues/563)
            'id': {'read_only': False},
        }

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{} - Level {}'.format(obj.dungeon.name, obj.floor)


class RosterSerializer(GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = herders.MonsterInstance
        fields = ['com2us_id', 'name', 'stars', 'level', 'notes']
        extra_kwargs = {
            'stars': {'read_only': True},
            'level': {'read_only': True},
            'notes': {'read_only': True},
        }

    name = serializers.SlugRelatedField(slug_field='name', source='monster', read_only=True)


class SummonerRosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = herders.Summoner
        fields = ['monsters']

    monsters = RosterSerializer(many=True, source='monsterinstance_set')


class MonsterSerializer(GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.OptimizeMonster
        fields = ['monster']

    monster = serializers.SlugRelatedField(slug_field='com2us_id', queryset=models.MonsterInstance.objects.all())


class SlowerThanBySerializer(GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.SpeedTune
        fields = ['slower_than', 'type', 'amount']

    slower_than = MonsterSerializer(match_on=['monster', 'team'])

    def save(self, **kwargs):
        """Need to pass team from parent (i.e. faster than) to child (i.e. slower_than)"""
        self._validated_data['slower_than']['team'] = self._validated_data['faster_than'].team
        return super().save(**kwargs)


class OptimizeMonsterSerializer(GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.OptimizeMonster
        fields = ['monster', 'leader', 'min_spd', 'min_hp', 'min_def', 'min_ehp',
                  'min_res', 'min_acc', 'min_crate', 'max_crate', 'slower_than_by']

    monster = RosterSerializer(match_on=['com2us_id'])
    slower_than_by = SlowerThanBySerializer(match_on=['faster_than', 'slower_than', 'type'], many=True)


class OptimizeTeamSerializer(RelatedSaveMixin, serializers.ModelSerializer):
    class Meta:
        model = models.OptimizeTeam
        fields = '__all__'

    owner = serializers.HiddenField(default=CurrentSummonerDefault())
    dungeon = DungeonSerializer(match_on=['id'])
    monsters = OptimizeMonsterSerializer(many=True, match_on=['team', 'monster'])
