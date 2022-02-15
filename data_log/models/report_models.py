from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from bestiary.models import Level, GameItem, BalancePatch, Monster
from data_log.models.log_models import CraftRuneLog, MagicBoxCraft
from herders.models import MonsterInstance, RuneBuild, RuneInstance


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
    
    def generate_report(self, monsters):
        categories = [
            "sets", "sets_4", "sets_2", 
            "slot_2", "slot_4", "slot_6", 
            "slots_2_4_6"
        ]

        build_attr = 'default_build'
        if self.is_rta:
            build_attr = 'rta_build'

        report = {
            "charts": {category: {"data": {}, "type": "occurrences", "total": 0,} for category in categories},
            "top": sorted(monsters, key=lambda m: getattr(m, build_attr).avg_efficiency, reverse=True)[:20],
        }
        mons_top = []
        for top in report["top"]:
            mons_top.append({
                'is_public': top.owner.consent_top,
                'obj': "", # TODO: temp, should be serializer
            })
        report["top"] = mons_top

        for monster in monsters:
            build = getattr(monster, build_attr)
            if not build:
                continue

            slot_2 = build.runes.filter(slot=2).first()
            slot_2_ms = slot_2.get_main_stat_display() if slot_2 else None
            if slot_2_ms:
                r_s_2 = report["charts"]["slot_2"]
                if slot_2_ms not in r_s_2["data"]:
                    r_s_2["data"][slot_2_ms] = 0
                r_s_2["data"][slot_2_ms] += 1
                
            slot_4 = build.runes.filter(slot=4).first()
            slot_4_ms = slot_4.get_main_stat_display() if slot_4 else None
            if slot_4_ms:
                r_s_4 = report["charts"]["slot_4"]
                if slot_4_ms not in r_s_4["data"]:
                    r_s_4["data"][slot_4_ms] = 0
                r_s_4["data"][slot_4_ms] += 1

            slot_6 = build.runes.filter(slot=6).first()
            slot_6_ms = slot_6.get_main_stat_display() if slot_6 else None
            if slot_6_ms:
                r_s_6 = report["charts"]["slot_6"]
                if slot_6_ms not in r_s_6["data"]:
                    r_s_6["data"][slot_6_ms] = 0
                r_s_6["data"][slot_6_ms] += 1

            slot_2_4_6 = ' / '.join([rune_ms if rune_ms else '-' for rune_ms in [slot_2_ms, slot_4_ms, slot_6_ms]])
            r_s_2_4_6 = report["charts"]["slots_2_4_6"]
            if slot_2_4_6 not in r_s_2_4_6["data"]:
                r_s_2_4_6["data"][slot_2_4_6] = 0
            r_s_2_4_6["data"][slot_2_4_6] += 1

            completed_sets = build.active_rune_sets
            for set_ in completed_sets:
                required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[set_]
                name = RuneInstance.TYPE_CHOICES[set_ - 1][1]
                if required == 4:
                    r_s_4 = report["charts"]["sets_4"]
                    if name not in r_s_4["data"]:
                        r_s_4["data"][name] = 0
                    r_s_4["data"][name] += 1
                elif required == 2:
                    r_s_4 = report["charts"]["sets_2"]
                    if name not in r_s_2["data"]:
                        r_s_2["data"][name] = 0
                    r_s_2["data"][name] += 1

            sets = build.rune_set_text
            r_s = report["charts"]["sets"]
            if sets not in r_s["data"]:
                r_s["data"][sets] = 0
            r_s["data"][sets] += 1

            for cat in categories:
                rep_cat = report["charts"][cat]
                rep_cat["data"] = {k: v for k, v in sorted(rep_cat["data"].items(), key=lambda item: item[1], reverse=True)}
                keys = list(rep_cat["data"].keys())
                proper_data = {k: v for k, v in rep_cat["data"].items() if k not in keys[5:]}
                other = sum([v for k, v in rep_cat["data"].items() if k in keys[5:]])
                rep_cat["data"] = {**proper_data, **{"Other": other}}
                rep_cat["total"] = sum([v for k, v in rep_cat["data"].items()])

        self.report = report
        self.save()
