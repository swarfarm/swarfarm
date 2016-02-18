import herders.models as herder_models


# Proxy models soley for admin organization purposes
class Monster(herder_models.Monster):
    class Meta:
        proxy = True


class Skill(herder_models.MonsterSkill):
    class Meta:
        proxy = True


class LeaderSkill(herder_models.MonsterLeaderSkill):
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


class ScalesWith(herder_models.MonsterSkillScalesWith):
    class Meta:
        proxy = True


class Source(herder_models.MonsterSource):
    class Meta:
        proxy = True


class Fusion(herder_models.Fusion):
    class Meta:
        proxy = True
