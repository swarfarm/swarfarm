from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_nested.relations import NestedHyperlinkedIdentityField

from herders.models import Summoner, Storage, BuildingInstance, MonsterInstance, MonsterPiece, RuneInstance, \
    RuneCraftInstance, TeamGroup, Team, RuneBuild


class AddOwnerOnCreate:
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.summoner


class RuneInstanceSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/runes-detail',
        parent_lookup_kwargs={'user_pk': 'owner__user__username'},
    )

    class Meta:
        model = RuneInstance
        fields = [
            'id', 'url', 'com2us_id', 'assigned_to',
            'type', 'slot', 'stars', 'level', 'quality', 'original_quality', 'value',
            'substat_upgrades_remaining', 'efficiency', 'max_efficiency',
            'main_stat', 'main_stat_value',
            'innate_stat', 'innate_stat_value',
            'substats', 'substat_values', 'substats_enchanted', 'substats_grind_value',
        ]


class RuneBuildSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/rune-builds-detail',
        parent_lookup_kwargs={'user_pk': 'owner__user__username'},
    )
    runes = RuneInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = RuneBuild
        fields = [
            'id',
            'url',
            'name',
            'monster',
            'runes',
            'hp',
            'hp_pct',
            'attack',
            'attack_pct',
            'defense',
            'defense_pct',
            'speed',
            'speed_pct',
            'crit_rate',
            'crit_damage',
            'resistance',
            'accuracy',
            'avg_efficiency',
        ]


class RuneCraftInstanceSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    class Meta:
        model = RuneCraftInstance
        fields = (
            'id',
            'com2us_id',
            'type',
            'rune',
            'stat',
            'quality',
            'value',
            'quantity',
        )


class MonsterInstanceSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    runes = RuneInstanceSerializer(many=True, read_only=True, source='runeinstance_set')
    # default_build = RuneBuildSerializer(read_only=True)
    # rta_build = RuneBuildSerializer(read_only=True)

    class Meta:
        model = MonsterInstance
        fields = [
            'id', 'com2us_id', 'created', 'monster', 'custom_name',
            'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'base_hp', 'base_attack', 'base_defense', 'base_speed', 'base_crit_rate', 'base_crit_damage', 'base_resistance', 'base_accuracy',
            'rune_hp', 'rune_attack', 'rune_defense', 'rune_speed', 'rune_crit_rate', 'rune_crit_damage', 'rune_resistance', 'rune_accuracy',
            'artifact_hp', 'artifact_attack', 'artifact_defense',
            'runes', 'default_build', 'rta_build', 'avg_rune_efficiency',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes',
        ]


class MonsterPieceSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/monster-pieces-detail',
        parent_lookup_kwargs={'user_pk': 'owner__user__username'},
    )

    class Meta:
        model = MonsterPiece
        fields = ['id', 'url', 'monster', 'pieces']


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = [
            'magic_essence', 'fire_essence', 'water_essence', 'wind_essence', 'light_essence', 'dark_essence',
            'wood', 'leather', 'rock', 'ore', 'mithril', 'cloth', 'rune_piece', 'dust',
            'symbol_harmony',  'symbol_transcendance', 'symbol_chaos',
            'crystal_water', 'crystal_fire', 'crystal_wind', 'crystal_light', 'crystal_dark', 'crystal_magic', 'crystal_pure',
            'fire_angelmon', 'water_angelmon', 'wind_angelmon', 'light_angelmon', 'dark_angelmon',
            'fire_king_angelmon', 'water_king_angelmon', 'wind_king_angelmon', 'light_king_angelmon', 'dark_king_angelmon',
            'rainbowmon_2_20', 'rainbowmon_3_1', 'rainbowmon_3_25', 'rainbowmon_4_1', 'rainbowmon_4_30', 'rainbowmon_5_1',
            'super_angelmon', 'devilmon',
        ]


class BuildingInstanceSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/buildings-detail',
        parent_lookup_kwargs={'user_pk': 'owner__user__username'},
    )

    class Meta:
        model = BuildingInstance
        fields = ['id', 'url', 'building', 'level']


class SummonerSerializer(serializers.ModelSerializer):
    server = serializers.ChoiceField(source='summoner.server', choices=Summoner.SERVER_CHOICES)
    public = serializers.BooleanField(source='summoner.public')

    class Meta:
        model = User
        fields = ['url', 'username', 'server', 'public']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'url': {
                'lookup_field': 'username',
                'lookup_url_kwarg': 'pk',
                'view_name': 'profiles-detail',
            },
        }


class FullUserSerializer(SummonerSerializer):
    email = serializers.EmailField(validators=[
        UniqueValidator(queryset=User.objects.all(), message='Email already in use.')
    ])
    timezone = serializers.CharField(source='summoner.timezone', allow_blank=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'password', 'email', 'is_staff', 'server', 'public', 'timezone']
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
        return super(FullUserSerializer, self).update(instance, validated_data)

    def create_or_update_summoner(self, user, summoner_data):
        summoner, created = Summoner.objects.get_or_create(user=user, defaults=summoner_data)

        if not created and summoner_data is not None:
            super(FullUserSerializer, self).update(summoner, summoner_data)


class TeamGroupSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/team-groups-detail',
        parent_lookup_kwargs={'user_pk': 'owner__user__username'},
    )

    teams = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True,
        source='team_set',
    )

    class Meta:
        model = TeamGroup
        fields = ['id', 'url', 'name', 'teams']


class TeamSerializer(serializers.ModelSerializer, AddOwnerOnCreate):
    url = NestedHyperlinkedIdentityField(
        view_name='profile/teams-detail',
        parent_lookup_kwargs={
            'user_pk': 'group__owner__user__username',
        },
    )

    leader = MonsterInstanceSerializer()
    roster = MonsterInstanceSerializer(many=True)

    class Meta:
        model = Team
        fields = ['id', 'url', 'group', 'favorite', 'name', 'description', 'leader', 'roster']