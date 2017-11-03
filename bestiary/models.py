from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.text import slugify

import herders.models as herder_models


class Dungeon(models.Model):
    TYPE_SCENARIO = 0
    TYPE_RUNE_DUNGEON = 1
    TYPE_ESSENCE_DUNGEON = 2
    TYPE_OTHER_DUNGEON = 3
    TYPE_RAID = 4
    TYPE_HALL_OF_HEROES = 5

    TYPE_CHOICES = [
        (TYPE_SCENARIO, 'Scenarios'),
        (TYPE_RUNE_DUNGEON, 'Rune Dungeons'),
        (TYPE_ESSENCE_DUNGEON, 'Elemental Dungeons'),
        (TYPE_OTHER_DUNGEON, 'Other Dungeons'),
        (TYPE_RAID, 'Raids'),
        (TYPE_HALL_OF_HEROES, 'Hall of Heroes'),
    ]

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=TYPE_CHOICES, blank=True, null=True)
    max_floors = models.IntegerField(default=10)
    slug = models.SlugField(blank=True, null=True)

    # For the following fields:
    # Outer array index is difficulty (normal, hard, hell). Inner array index is the stage/floor
    # Example: Hell B2 is dungeon.energy_cost[RunLog.DIFFICULTY_HELL][1]
    energy_cost = ArrayField(ArrayField(models.IntegerField(blank=True, null=True)), blank=True, null=True)
    xp = ArrayField(ArrayField(models.IntegerField(blank=True, null=True)), blank=True, null=True)
    monster_slots = ArrayField(ArrayField(models.IntegerField(blank=True, null=True)), blank=True, null=True)

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Dungeon, self).save(*args, **kwargs)


# Proxy models solely for admin organization purposes
class Building(herder_models.Building):
    class Meta:
        proxy = True


class CraftMaterial(herder_models.CraftMaterial):
    class Meta:
        proxy = True


class MonsterCraftCost(herder_models.MonsterCraftCost):
    class Meta:
        proxy = True


class HomunculusSkillCraftCost(herder_models.HomunculusSkillCraftCost):
    class Meta:
        proxy = True


class Monster(herder_models.Monster):
    class Meta:
        proxy = True


class Source(herder_models.MonsterSource):
    class Meta:
        proxy = True


class Skill(herder_models.MonsterSkill):
    class Meta:
        proxy = True


class LeaderSkill(herder_models.MonsterLeaderSkill):
    class Meta:
        proxy = True


class HomunculusSkill(herder_models.HomunculusSkill):
    class Meta:
        proxy = True


class Effect(herder_models.MonsterSkillEffect):
    class Meta:
        proxy = True


class EffectDetail(herder_models.MonsterSkillEffectDetail):
    class Meta:
        proxy = True


class ScalingStat(herder_models.MonsterSkillScalingStat):
    class Meta:
        proxy = True


class Fusion(herder_models.Fusion):
    class Meta:
        proxy = True


class PatchNotes(models.Model):
    major = models.IntegerField()
    minor = models.IntegerField()
    dev = models.IntegerField()
    description = models.CharField(max_length=60, blank=True, null=True)
    timestamp = models.DateTimeField()
    detailed_notes = models.TextField(blank=True, null=True)
    data_tables = JSONField(blank=True, null=True)
    data_table_changes = JSONField(blank=True, null=True)

    def __str__(self):
        return '{}.{}.{} - {}'.format(self.major, self.minor, self.dev, self.description)
