from django.db import models

import herders.models as herder_models


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

    def __str__(self):
        return '{}.{}.{} - {}'.format(self.major, self.minor, self.dev, self.description)
