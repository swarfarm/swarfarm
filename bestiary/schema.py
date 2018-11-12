import graphene
from graphene_django.types import DjangoObjectType

from herders.models import Monster, MonsterSkill as Skill, MonsterSkillEffect as Effect, \
    MonsterSkillEffectDetail as EffectDetail
from .models import Dungeon, Level


class DungeonType(DjangoObjectType):
    class Meta:
        model = Dungeon


class LevelType(DjangoObjectType):
    class Meta:
        model = Level


class MonsterObjectType(DjangoObjectType):
    base_stars = graphene.Int()

    class Meta:
        model = Monster


class SkillObjectType(DjangoObjectType):
    class Meta:
        model = Skill


class EffectObjectType(DjangoObjectType):
    class Meta:
        model = Effect


class EffectDetailObjectType(DjangoObjectType):
    class Meta:
        model = EffectDetail


class Query(object):
    dungeon = graphene.Field(DungeonType, id=graphene.Int())
    all_dungeons = graphene.List(DungeonType)

    def resolve_dungeon(self, info, id, **kwargs):
        return Dungeon.objects.get(pk=id)

    def resolve_all_dungeons(self, info, **kwargs):
        return Dungeon.objects.all()

    level = graphene.Field(LevelType, id=graphene.Int())
    all_levels = graphene.List(LevelType)

    def resolve_level(self, info, id, **kwargs):
        return Level.objects.get(pk=id)

    def resolve_all_levels(self, info, **kwargs):
        return Level.objects.all().select_related('dungeon')

    monster = graphene.Field(MonsterObjectType, id=graphene.Int())
    all_monsters = graphene.List(MonsterObjectType)

    def resolve_monster(self, info, id, **kwargs):
        return Monster.objects.get(pk=id).select_related('awakens_from', 'awakens_to').prefetch_related('skills', 'skills__effect')

    def resolve_all_monsters(self, info, **kwargs):
        return Monster.objects.all().select_related('awakens_from', 'awakens_to').prefetch_related('skills', 'skills__effect')

    skill = graphene.Field(SkillObjectType, id=graphene.Int())
    all_skills = graphene.List(SkillObjectType)

    def resolve_skill(self, info, id, **kwargs):
        return Skill.objects.get(pk=id)

    def resolve_all_skills(self, info, **kwargs):
        return Skill.objects.all()

    skill_effect = graphene.Field(EffectObjectType, id=graphene.Int())
    all_skill_effects = graphene.List(EffectObjectType)

    def resolve_skill_effect(self, info, id, **kwargs):
        return Effect.objects.get(pk=id)

    def resolve_all_skill_effects(self, info, **kwargs):
        return Effect.objects.all()
