from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_nested.relations import NestedHyperlinkedIdentityField

from herders.models import Summoner, Storage, BuildingInstance, MonsterInstance, MonsterPiece, RuneInstance, RuneCraftInstance, TeamGroup, Team


class RuneInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/runes-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )
    # owner = serializers.HyperlinkedRelatedField(view_name='profiles-detail', source='owner.user.username', read_only=True)
    # TODO: Fix owner field so as not to cause a query explosion

    class Meta:
        model = RuneInstance
        fields = [
            'id', 'url', 'com2us_id', 'assigned_to',
            'type', 'slot', 'stars', 'level', 'quality', 'original_quality', 'value',
            'substat_upgrades_remaining', 'efficiency', 'max_efficiency',
            'main_stat', 'main_stat_value',
            'innate_stat', 'innate_stat_value',
            'substat_1', 'substat_1_value', 'substat_1_craft',
            'substat_2', 'substat_2_value', 'substat_2_craft',
            'substat_3', 'substat_3_value', 'substat_3_craft',
            'substat_4', 'substat_4_value', 'substat_4_craft',
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner
        return super(RuneInstanceSerializer, self).create(validated_data)


class RuneCraftInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/rune-crafts-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    class Meta:
        model = RuneCraftInstance
        fields = ['id', 'url', 'com2us_id', 'type', 'rune', 'stat', 'quality', 'value']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner
        return super(RuneCraftInstanceSerializer, self).create(validated_data)


class MonsterInstanceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/monsters-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )
    # owner = serializers.HyperlinkedRelatedField(view_name='profiles-detail', source='owner.user.username', read_only=True)
    # TODO: Fix owner field so as not to cause a query explosion
    runes = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='runeinstance_set')

    class Meta:
        model = MonsterInstance
        fields = [
            'id', 'url', 'com2us_id', 'created', 'monster',
            'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'base_hp', 'base_attack', 'base_defense', 'base_speed', 'base_crit_rate', 'base_crit_damage', 'base_resistance', 'base_accuracy',
            'rune_hp', 'rune_attack', 'rune_defense', 'rune_speed', 'rune_crit_rate', 'rune_crit_damage', 'rune_resistance', 'rune_accuracy',
            'avg_rune_efficiency', 'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes', 'runes',
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner
        return super(MonsterInstanceSerializer, self).create(validated_data)


class MonsterPieceSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/monster-pieces-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    class Meta:
        model = MonsterPiece
        fields = ['id', 'url', 'monster', 'pieces']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner
        return super(MonsterPieceSerializer, self).create(validated_data)


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
        view_name='profile/buildings-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    class Meta:
        model = BuildingInstance
        fields = ['id', 'url', 'building', 'level']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner
        return super(BuildingInstanceSerializer, self).create(validated_data)


class SummonerSummarySerializer(serializers.ModelSerializer):
    in_game_name = serializers.CharField(source='summoner.summoner_name', allow_blank=True)
    server = serializers.ChoiceField(source='summoner.server', choices=Summoner.SERVER_CHOICES)
    public = serializers.BooleanField(source='summoner.public')

    class Meta:
        model = User
        fields = ['url', 'username', 'in_game_name', 'server', 'public']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'profiles-detail',
            },
        }


class SummonerSerializer(serializers.ModelSerializer):
    in_game_name = serializers.CharField(source='summoner.summoner_name', allow_blank=True)
    server = serializers.ChoiceField(source='summoner.server', choices=Summoner.SERVER_CHOICES)
    public = serializers.BooleanField(source='summoner.public')
    timezone = serializers.CharField(source='summoner.timezone', allow_blank=True)
    # storage = StorageSerializer(source='summoner.storage')

    class Meta:
        model = User
        fields = ['url', 'username', 'password', 'email', 'is_staff', 'in_game_name', 'server', 'public', 'timezone']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
            },
            'is_staff': {'read_only': True},
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'profiles-detail',
            },
        }

    def create(self, validated_data):
        summoner_data = validated_data.pop('summoner', None)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        self.create_or_update_summoner(user, summoner_data)
        user.save()

        return user

    def update(self, instance, validated_data):
        summoner_data = validated_data.pop('summoner', None)
        self.create_or_update_summoner(instance, summoner_data)
        return super(SummonerSerializer, self).update(instance, validated_data)

    def create_or_update_summoner(self, user, summoner_data):
        summoner, created = Summoner.objects.get_or_create(user=user, defaults=summoner_data)

        if not created and summoner_data is not None:
            super(SummonerSerializer, self).update(summoner, summoner_data)


class TeamGroupSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/team-groups-detail',
        parent_lookup_kwargs={'summoner_pk': 'owner__user__username'},
    )

    teams = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True,
        source='team_set',
    )

    class Meta:
        model = TeamGroup
        fields = ['id', 'url', 'name', 'teams']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner
        return super(TeamGroupSerializer, self).create(validated_data)


class TeamSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/teams-detail',
        parent_lookup_kwargs={
            'summoner_pk': 'group__owner__user__username',
        },
    )

    class Meta:
        model = Team
        fields = ['id', 'url', 'group', 'favorite', 'name', 'description', 'leader', 'roster']