from django.db import models

from bestiary.models import Level
from herders.models import MonsterInstance, Monster, RuneInstance, Summoner
from sw_parser.models import RunLog


class MonsterStatTargets(models.Model):
    monster = models.ForeignKey(MonsterInstance, on_delete=models.CASCADE)
    # SPD
    min_spd = models.PositiveSmallIntegerField(blank=True, null=True)
    max_spd = models.PositiveSmallIntegerField(blank=True, null=True)
    # Survivability
    min_hp = models.PositiveIntegerField(blank=True, null=True)
    min_def = models.PositiveSmallIntegerField(blank=True, null=True)
    min_ehp = models.PositiveIntegerField(blank=True, null=True)
    min_ehp_d = models.PositiveIntegerField(blank=True, null=True)
    min_res = models.PositiveSmallIntegerField(blank=True, null=True)
    max_hp = models.PositiveIntegerField(blank=True, null=True)
    max_def = models.PositiveSmallIntegerField(blank=True, null=True)
    max_ehp = models.PositiveIntegerField(blank=True, null=True)
    max_ehp_d = models.PositiveIntegerField(blank=True, null=True)
    max_res = models.PositiveSmallIntegerField(blank=True, null=True)
    # DMG
    min_acc = models.PositiveSmallIntegerField(blank=True, null=True)
    min_atk = models.PositiveSmallIntegerField(blank=True, null=True)
    min_cdmg = models.PositiveSmallIntegerField(blank=True, null=True)
    min_crate = models.PositiveSmallIntegerField(blank=True, null=True)
    min_dps = models.PositiveIntegerField(blank=True, null=True)
    max_acc = models.PositiveSmallIntegerField(blank=True, null=True)
    max_atk = models.PositiveSmallIntegerField(blank=True, null=True)
    max_crate = models.PositiveSmallIntegerField(blank=True, null=True)
    max_cdmg = models.PositiveSmallIntegerField(blank=True, null=True)
    max_dps = models.PositiveIntegerField(blank=True, null=True)
    # Rune Quality
    min_rune_avg = models.FloatField(blank=True, null=True)
    max_rune_avg = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True


class RelativeSpeed(models.Model):
    SPD_ANY_AMOUNT = 0
    SPD_AS_LITTLE_AS_POSSIBLE = 1
    SPD_WITHIN_PERCENT = 2
    SPD_WITHIN_FLAT = 3
    SPD_AT_LEAST_FLAT = 4  # leaders with equal speed are always faster so they need to be at least one slower

    CHOICES_TUNE = [
        (SPD_ANY_AMOUNT, 'by Any Amount'),
        (SPD_AS_LITTLE_AS_POSSIBLE, 'by as Little as Possible'),
        (SPD_WITHIN_PERCENT, 'but within % SPD'),
        (SPD_WITHIN_FLAT, 'but within flat SPD'),
    ]

    type = models.IntegerField(choices=CHOICES_TUNE)
    amount = models.IntegerField(null=True)

    class Meta:
        abstract = True


class OptimizeTeam(models.Model):
    """The nexus for an optimized team"""
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    dungeon = models.ForeignKey(Level, on_delete=models.CASCADE, null=True)
    name = models.TextField()


class OptimizeMonster(MonsterStatTargets):
    team = models.ForeignKey(OptimizeTeam, on_delete=models.CASCADE, related_name='monsters')
    leader = models.BooleanField(default=False)
    slower_than = models.ManyToManyField('self', through='SpeedTune', related_name='faster_than', symmetrical=False)


class SpeedTune(RelativeSpeed):
    slower_than = models.ForeignKey(OptimizeMonster, on_delete=models.CASCADE, related_name='faster_than_by')
    faster_than = models.ForeignKey(OptimizeMonster, on_delete=models.CASCADE, related_name='slower_than_by')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """If a leader needs to move after another unit, it must be slower than that unit by at least 1"""
        if self.type != self.SPD_AT_LEAST_FLAT and self.faster_than.leader:
            # make sure a minimum amount exists
            has_by_one = self.faster_than.slower_than_by.filter(
                self.slower_than, self.faster_than, type=self.SPD_AT_LEAST_FLAT
            ).exists()
            if not has_by_one:
                SpeedTune.objects.create(
                    faster_than=self.faster_than,
                    slower_than=self.slower_than,
                    type=self.SPD_AT_LEAST_FLAT,
                    amount=1,
                )
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
