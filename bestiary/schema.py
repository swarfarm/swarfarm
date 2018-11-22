import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from herders.models import Monster, MonsterSkill as Skill, MonsterSkillEffect as Effect, \
    MonsterSkillEffectDetail as EffectDetail
from .models import Dungeon, Level


class DungeonNode(DjangoObjectType):
    class Meta:
        model = Dungeon
        interfaces = (relay.Node,)
        filter_fields = [
            'id',
            'name',
            'category',
        ]

class LevelNode(DjangoObjectType):
    class Meta:
        model = Level
        interfaces = (relay.Node,)
        filter_fields = []


class MonsterNode(DjangoObjectType):
    base_stars = graphene.Int()

    class Meta:
        model = Monster
        interfaces = (relay.Node,)
        filter_fields = []


class SkillNode(DjangoObjectType):
    class Meta:
        model = Skill
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


class Query(object):
    dungeon = relay.Node.Field(DungeonNode, id=graphene.Int())
    all_dungeons = DjangoFilterConnectionField(DungeonNode)

    def resolve_dungeon(self, info, id, **kwargs):
        return Dungeon.objects.get(pk=id)

    def resolve_all_dungeons(self, info, **kwargs):
        return Dungeon.objects.all()

    level = relay.Node.Field(LevelNode, id=graphene.Int())
    all_levels = DjangoFilterConnectionField(LevelNode, )

    def resolve_level(self, info, id, **kwargs):
        return Level.objects.get(pk=id)

    def resolve_all_levels(self, info, **kwargs):
        return Level.objects.all().select_related('dungeon')

    monster = relay.Node.Field(MonsterNode, id=graphene.Int())
    all_monsters = DjangoFilterConnectionField(
        MonsterNode,
        max_limit=200
    )

    def resolve_monster(self, info, id, **kwargs):
        return Monster.objects.get(pk=id).select_related('awakens_from', 'awakens_to').prefetch_related('skills', 'skills__effect')

    def resolve_all_monsters(self, info, first=100, **kwargs):
        return Monster.objects.all().select_related('awakens_from', 'awakens_to').prefetch_related('skills', 'skills__effect')

    skill = relay.Node.Field(SkillNode, id=graphene.Int())
    all_skills = DjangoFilterConnectionField(SkillNode)

    def resolve_skill(self, info, id, **kwargs):
        return Skill.objects.get(pk=id)

    def resolve_all_skills(self, info, **kwargs):
        return Skill.objects.all()

    skill_effect = relay.Node.Field(EffectNode, id=graphene.Int())
    all_skill_effects = DjangoFilterConnectionField(EffectNode)

    def resolve_skill_effect(self, info, id, **kwargs):
        return Effect.objects.get(pk=id)

    def resolve_all_skill_effects(self, info, **kwargs):
        return Effect.objects.all()
