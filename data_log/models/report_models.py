from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from bestiary.models import Level, GameItem, BalancePatch, Monster
from data_log.models.log_models import CraftRuneLog, MagicBoxCraft
from herders.models import MonsterInstance, RuneBuild


class Report(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The logging model used to generate this report"
    )
    generated_on = models.DateTimeField(auto_now_add=True)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    log_count = models.IntegerField()
    unique_contributors = models.IntegerField()
    report = JSONField()

    class Meta:
        get_latest_by = 'generated_on'

    def __str__(self):
        return f"{self.generated_on} - {self.content_type}"


class LevelReport(Report):
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='logs')

    def __str__(self):
        return f"{self.level} {self.generated_on}"


class SummonReport(Report):
    item = models.ForeignKey(GameItem, on_delete=models.PROTECT)


class MagicShopRefreshReport(Report):
    pass


class MagicBoxCraftingReport(Report):
    box_type = models.IntegerField(choices=MagicBoxCraft.BOX_CHOICES)


class WishReport(Report):
    pass


class RuneCraftingReport(Report):
    craft_level = models.IntegerField(choices=CraftRuneLog.CRAFT_CHOICES)


class StatisticsReport(models.Model):
    SERVER_GLOBAL = 0
    SERVER_EUROPE = 1
    SERVER_ASIA = 2
    SERVER_KOREA = 3
    SERVER_JAPAN = 4
    SERVER_CHINA = 5

    SERVER_CHOICES = [
        (SERVER_GLOBAL, 'Global'),
        (SERVER_EUROPE, 'Europe'),
        (SERVER_ASIA, 'Asia'),
        (SERVER_KOREA, 'Korea'),
        (SERVER_JAPAN, 'Japan'),
        (SERVER_CHINA, 'China'),
    ]

    generated_on = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    is_rta = models.BooleanField(default=False)
    min_box_6stars = models.IntegerField(default=0)
    server = models.IntegerField(choices=SERVER_CHOICES, null=True, blank=True)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    report = JSONField()

    @property
    def included_balance_patches(self):
        return BalancePatch.objects.filter(date__gt=self.start_date, date__lt=self.generated_on.date())
    
    def __str__(self):
        return f'{self.monster}, {self.start_date}, {self.server if self.server else "All"}, {"RTA" if self.is_rta else "Default"}, {self.min_box_6stars}+ 6*'

    class Meta:
        unique_together = (('monster', 'start_date', 'is_rta', 'min_box_6stars', 'server'),)
        get_latest_by = 'start_date'
    
    def monsterinstances(self, profiles, filter_by_date=True):
        # this method doesn't filter by min_box_6stars and server - performance issues
        if filter_by_date:
            profiles = profiles.filter(last_update__date__gte=self.start_date)
        profiles_f = profiles.filter(monsterinstance__monster=self.monster)

        monsters_t_pks = profiles_f.values_list('monsterinstance', flat=True)
        monsters_t = MonsterInstance.objects.filter(pk__in=monsters_t_pks)
        if self.is_rta:
            builds = monsters_t.filter(rta_build__isnull=False).values_list('rta_build', flat=True)
        else:
            builds = monsters_t.filter(default_build__isnull=False).values_list('default_build', flat=True)
        
        monsters_b_pks = RuneBuild.objects.filter(pk__in=builds).annotate(c=models.Count('runes')).filter(c=6).distinct().values_list('monster', flat=True)
        data_monsters = MonsterInstance.objects.filter(pk__in=monsters_b_pks)
        monsters = []
        for monster in data_monsters:
            monster_update = monster.owner.last_update.date()
            bps = self.included_balance_patches.filter(monsters=monster.monster)
            if bps.exists():
                if monster_update > bps.latest().date:
                    monsters.append(monster)
                    continue
            elif monster_update >= self.start_date:
                    monsters.append(monster)
                    continue

        return monsters
