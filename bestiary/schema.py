import graphene
from graphene_django.types import DjangoObjectType

from .models import Dungeon, Level


class DungeonType(DjangoObjectType):
    class Meta:
        model = Dungeon


class LevelType(DjangoObjectType):
    class Meta:
        model = Level


class Query(object):
    all_dungeons = graphene.List(DungeonType)
    all_levels = graphene.List(LevelType)

    def resolve_all_dungeons(self, info, **kwargs):
        return Dungeon.objects.all()

    def resolve_all_levels(self, info, **kwargs):
        return Level.objects.select_related('dungeon').all()
