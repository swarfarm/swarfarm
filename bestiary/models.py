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
    max_floors = models.IntegerField(default=10)
    slug = models.SlugField(blank=True, null=True)

    # TODO: Remove following fields when Level model is fully utilized everywhere: type, energy_cost, xp, monster_slots
    type = models.IntegerField(choices=TYPE_CHOICES, blank=True, null=True)
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


class Level(models.Model):
    DIFFICULTY_NORMAL = 1
    DIFFICULTY_HARD = 2
    DIFFICULTY_HELL = 3
    DIFFICULTY_CHOICES = (
        (DIFFICULTY_NORMAL, 'Normal'),
        (DIFFICULTY_HARD, 'Hard'),
        (DIFFICULTY_HELL, 'Hell'),
    )

    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE)
    floor = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, blank=True, null=True)
    energy_cost = models.IntegerField(blank=True, null=True, help_text='Energy cost to start a run')
    xp = models.IntegerField(blank=True, null=True, help_text='XP gained by fully clearing the level')
    frontline_slots = models.IntegerField(
        default=5,
        help_text='Serves as general slots if dungeon does not have front/back lines'
    )
    backline_slots = models.IntegerField(blank=True, null=True, help_text='Leave null for normal dungeons')
    max_slots = models.IntegerField(
        blank=True,
        null=True,
        help_text='Maximum monsters combined front/backline. Not required if backline not specified.'
    )

    class Meta:
        ordering = ('difficulty', 'floor')
        unique_together = ('dungeon', 'floor', 'difficulty')

    def __str__(self):
        return f'{self.dungeon_id} {self.floor} - {self.get_difficulty_display()}'

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
