import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from .api_filters import MonsterFilter, SkillFilter
from .models import Monster, MonsterLeaderSkill as LeaderSkill, MonsterSkill as Skill, \
    MonsterSkillEffect as Effect, MonsterSkillEffectDetail as EffectDetail, MonsterSource as Source, \
    MonsterSkillScalingStat as ScalingStat, MonsterCraftCost, CraftMaterial, Dungeon, Level


class LevelNode(DjangoObjectType):
    class Meta:
        model = Level
        interfaces = (relay.Node,)
        filter_fields = []


class DungeonNode(DjangoObjectType):
    class Meta:
        model = Dungeon
        description = "Dungeon objects"
        interfaces = (relay.Node,)
        only_fields = [
            'id',
            'name',
            'max_floors',
            'slug',
            'category',
            'levels',
        ]
        filter_fields = [
            'id',
            'name',
            'category',
        ]


class LeaderSkillNode(DjangoObjectType):
    class Meta:
        model = LeaderSkill
        interfaces = (relay.Node,)
        filter_fields = []


class EffectNode(DjangoObjectType):
    class Meta:
        model = Effect
        interfaces = (relay.Node,)
        filter_fields = []


class EffectDetailNode(DjangoObjectType):
    class Meta:
        model = EffectDetail
        interfaces = (relay.Node,)
        filter_fields = []


class ScalingStatNode(DjangoObjectType):
    class Meta:
        model = ScalingStat
        interfaces = (relay.Node,)
        filter_fields = []
        only_fields = [
            'stat',
            'com2us_desc',
            'description',
        ]


class SkillNode(DjangoObjectType):
    effects = graphene.List(of_type=EffectDetailNode)
    scaling_stats = graphene.List(of_type=ScalingStatNode)

    def resolve_effects(self, info, *args, **kwargs):
        return self.monsterskilleffectdetail_set.all()

    def resolve_scaling_stats(self, info, *args, **kwargs):
        return self.scaling_stats.all()

    class Meta:
        model = Skill
        interfaces = (relay.Node,)
        only_fields = [
            'id',
            'name',
            'com2us_id',
            'description',
            'slot',
            'effects',
            'cooltime',
            'hits',
            'aoe',
            'passive',
            'max_level',
            'level_progress_description',
            'icon_filename',
            'multiplier_formula',
            'multiplier_formula_raw',
            'scaling_stats',
        ]


class SourceNode(DjangoObjectType):
    class Meta:
        model = Source
        interfaces = (relay.Node,)
        filter_fields = []


class MonsterCraftCostNode(DjangoObjectType):
    class Meta:
        model = MonsterCraftCost
        interfaces = (relay.Node,)
        filter_fields = []


class CraftMaterialNode(DjangoObjectType):
    class Meta:
        model = CraftMaterial
        interfaces = (relay.Node,)
        filter_fields = []


class MonsterNode(DjangoObjectType):
    base_stars = graphene.Int()
    skills = graphene.List(of_type=SkillNode)

    def resolve_skills(self, *args, **kwargs):
        return self.skills.all()

    class Meta:
        model = Monster
        interfaces = (relay.Node,)
        only_fields = [
            'id',
            'name',
            'com2us_id',
            'family_id',
            'image_filename',
            'element',
            'archetype',
            'base_stars',
            'obtainable',
            'can_awaken',
            'is_awakened',
            'awaken_bonus',
            'skills',
            'skill_ups_to_max',
            'leader_skill',
            'raw_hp',
            'raw_attack',
            'raw_defense',
            'base_hp',
            'base_attack',
            'base_defense',
            'max_lvl_hp',
            'max_lvl_attack',
            'max_lvl_defense',
            'speed',
            'crit_rate',
            'crit_damage',
            'resistance',
            'accuracy',
            'homunculus',
            'monstercraftcost_set',
            'craft_cost',
            'transforms_into',
            'awakens_from',
            'awakens_to',
            'awaken_mats_fire_low',
            'awaken_mats_fire_mid',
            'awaken_mats_fire_high',
            'awaken_mats_water_low',
            'awaken_mats_water_mid',
            'awaken_mats_water_high',
            'awaken_mats_wind_low',
            'awaken_mats_wind_mid',
            'awaken_mats_wind_high',
            'awaken_mats_light_low',
            'awaken_mats_light_mid',
            'awaken_mats_light_high',
            'awaken_mats_dark_low',
            'awaken_mats_dark_mid',
            'awaken_mats_dark_high',
            'awaken_mats_magic_low',
            'awaken_mats_magic_mid',
            'awaken_mats_magic_high',
            'source',
            'farmable',
            'fusion_food',
            'bestiary_slug'
        ]


def _optimized_monster_queryset():
    return Monster.objects.all().select_related(
        'leader_skill',
        'awakens_from',
        'awakens_to',
        'transforms_into',
    ).prefetch_related(
        'skills',
        'skills__effect',
        'skills__effect__effect',
        'skills__scaling_stats',
        'monstercraftcost_set',
        'monstercraftcost_set__craft',
        'source',
    )


def _optimized_skill_queryset():
    return Skill.objects.all().prefetch_related(
        'scaling_stats',
        'monsterskilleffectdetail_set',
        'monsterskilleffectdetail_set__effect',
        'monsterskilleffectdetail_set__effect__effect',
    )


class Query(object):
    dungeon = relay.Node.Field(DungeonNode)
    all_dungeons = DjangoFilterConnectionField(DungeonNode)

    def resolve_dungeon(self, info, id, **kwargs):
        return Dungeon.objects.prefetch_related('level_set').get(pk=id)

    def resolve_all_dungeons(self, info, **kwargs):
        return Dungeon.objects.all().prefetch_related('level_set')

    level = relay.Node.Field(LevelNode)
    all_levels = DjangoFilterConnectionField(LevelNode, )

    def resolve_level(self, info, id, **kwargs):
        return Level.objects.select_related('dungeon').get(pk=id)

    def resolve_all_levels(self, info, **kwargs):
        return Level.objects.all().select_related('dungeon')

    monster = relay.Node.Field(MonsterNode)
    all_monsters = DjangoFilterConnectionField(
        MonsterNode,
        filterset_class=MonsterFilter,
        max_limit=200,
        enforce_first_or_last=True,
    )

    def resolve_monster(self, info, id, **kwargs):
        return _optimized_monster_queryset().get(pk=id)

    def resolve_all_monsters(self, info, **kwargs):
        return _optimized_monster_queryset()

    source = graphene.Field(SourceNode)
    all_sources = DjangoFilterConnectionField(SourceNode)

    craftCost = relay.Node.Field(MonsterCraftCostNode)
    craftMaterial = relay.Node.Field(CraftMaterialNode)

    leader_skill = relay.Node.Field(LeaderSkillNode)

    skill = relay.Node.Field(SkillNode)
    all_skills = DjangoFilterConnectionField(
        SkillNode,
        filterset_class=SkillFilter,
        max_limit=200,
        enforce_first_or_last=True,
    )

    def resolve_skill(self, info, id, **kwargs):
        return _optimized_skill_queryset().get(pk=id)

    def resolve_all_skills(self, info, **kwargs):
        return _optimized_skill_queryset()

    skill_effect = relay.Node.Field(EffectNode)
    all_skill_effects = DjangoFilterConnectionField(EffectNode)

    scaling_stat = relay.Node.Field(ScalingStatNode)
    all_scaling_stats = DjangoFilterConnectionField(ScalingStatNode)
