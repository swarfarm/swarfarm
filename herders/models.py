import uuid
from collections import OrderedDict
from math import floor, ceil

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Count, Avg
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from timezone_field import TimeZoneField

from bestiary.models import base, Monster, Building, Level, Rune, RuneCraft, Artifact, ArtifactCraft, GameItem


# Individual user/monster collection models
class Summoner(models.Model):
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    summoner_name = models.CharField(max_length=256, null=True, blank=True)
    com2us_id = models.BigIntegerField(default=None, null=True, blank=True)
    server = models.IntegerField(choices=SERVER_CHOICES, default=SERVER_GLOBAL, null=True, blank=True)
    following = models.ManyToManyField("self", related_name='followed_by', symmetrical=False)
    public = models.BooleanField(default=False, blank=True)
    timezone = TimeZoneField(default='America/Los_Angeles')
    notes = models.TextField(null=True, blank=True)
    preferences = JSONField(default=dict, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_rune_counts(self):
        counts = {}

        for rune_type in RuneInstance.TYPE_CHOICES:
            counts[rune_type[1]] = RuneInstance.objects.filter(owner=self, type=rune_type[0]).count()

        return counts

    def save(self, *args, **kwargs):
        super(Summoner, self).save(*args, **kwargs)

        # TODO: update Storage to new db 
        # Update new storage model
        # if not hasattr(self, 'storage'):
        #     new_storage = Storage.objects.create(
        #         owner=self,
        #     )
        #     new_storage.save()

    def __str__(self):
        return self.user.username


def _default_storage_data():
    return [0, 0, 0]

class MaterialStorage(models.Model):
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    item = models.ForeignKey(GameItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


    @staticmethod
    def _min_zero(x):
        return max(x, 0)

    def save(self, *args, **kwargs):
        self.quantity = map(self._min_zero, self.quantity)
        super(Storage, self).save(*args, **kwargs)

class MonsterShrineStorage(models.Model):
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    item = models.ForeignKey(Monster, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    @staticmethod
    def _min_zero(x):
        return max(x, 0)

    def save(self, *args, **kwargs):
        self.quantity = map(self._min_zero, self.quantity)
        super(Storage, self).save(*args, **kwargs)


class MonsterTag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return mark_safe(self.name)


class MonsterInstance(models.Model, base.Stars):
    PRIORITY_DONE = 0
    PRIORITY_LOW = 1
    PRIORITY_MED = 2
    PRIORITY_HIGH = 3

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MED, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    com2us_id = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    stars = models.IntegerField(choices=base.Stars.STAR_CHOICES)
    level = models.IntegerField()
    skill_1_level = models.IntegerField(blank=True, default=1)
    skill_2_level = models.IntegerField(blank=True, default=1)
    skill_3_level = models.IntegerField(blank=True, default=1)
    skill_4_level = models.IntegerField(blank=True, default=1)
    fodder = models.BooleanField(default=False)
    in_storage = models.BooleanField(default=False)
    ignore_for_fusion = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, blank=True, null=True)
    tags = models.ManyToManyField(MonsterTag, blank=True)
    notes = models.TextField(null=True, blank=True, help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    custom_name = models.CharField(default='', max_length=20, blank=True)
    default_build = models.ForeignKey('RuneBuild', null=True, on_delete=models.SET_NULL, related_name='default_build')
    rta_build = models.ForeignKey('RuneBuild', null=True, on_delete=models.SET_NULL, related_name='rta_build')

    # Calculated fields (on save)
    rune_hp = models.IntegerField(blank=True, default=0)
    rune_attack = models.IntegerField(blank=True, default=0)
    rune_defense = models.IntegerField(blank=True, default=0)
    rune_speed = models.IntegerField(blank=True, default=0)
    rune_crit_rate = models.IntegerField(blank=True, default=0)
    rune_crit_damage = models.IntegerField(blank=True, default=0)
    rune_resistance = models.IntegerField(blank=True, default=0)
    rune_accuracy = models.IntegerField(blank=True, default=0)
    avg_rune_efficiency = models.FloatField(blank=True, null=True)
    artifact_hp = models.IntegerField(blank=True, default=0)
    artifact_attack = models.IntegerField(blank=True, default=0)
    artifact_defense = models.IntegerField(blank=True, default=0)

    class Meta:
        ordering = ['-stars', '-level', 'monster__name']

    def __str__(self):
        return f'{self.get_stars_display()} {self.monster} Lv. {self.level}'

    def is_max_level(self):
        return self.level == self.monster.max_level_from_stars(self.stars)

    def max_level_from_stars(self):
        return self.monster.max_level_from_stars(self.stars)

    def skill_ups_to_max(self):
        skill_ups_remaining = self.monster.skill_ups_to_max or 0
        skill_levels = [self.skill_1_level, self.skill_2_level, self.skill_3_level, self.skill_4_level]

        for idx in range(0, self.monster.skills.count()):
            skill_ups_remaining -= skill_levels[idx] - 1

        return skill_ups_remaining

    def get_rune_set_summary(self):
        sets = []

        # Determine rune sets
        rune_counts = self.runeinstance_set.values('type').order_by().annotate(count=Count('type'))
        num_equipped = self.runeinstance_set.count()

        for rune_count in rune_counts:
            type_name = RuneInstance.TYPE_CHOICES[rune_count['type'] - 1][1]
            required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[rune_count['type']]
            present = rune_count['count']

            if present >= required:
                num_equipped -= required * (present // required)
                sets += [type_name] * (present // required)

        if num_equipped:
            # Some runes are present that aren't in a set
            sets.append('Broken')

        # Summarize slot 2/4/6 main stats
        stats = []

        for x in [2, 4, 6]:
            try:
                stats.append(self.runeinstance_set.get(slot=x).get_main_stat_display())
            except:
                continue

        return '/'.join(sets) + ' - ' + '/'.join(stats)

    def get_rune_set_bonuses(self):
        rune_counts = self.runeinstance_set.values('type').order_by().annotate(count=Count('type'))
        rune_bonuses = []

        for rune_count in rune_counts:
            required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[rune_count['type']]
            present = rune_count['count']
            bonus_text = RuneInstance.RUNE_SET_BONUSES[rune_count['type']]['description']

            if present >= required:
                rune_bonuses.extend([bonus_text] * (present // required))

        return rune_bonuses

    def get_avg_rune_efficiency(self):
        # TODO: Switch after switching to rune builds
        # return self.default_build.avg_efficiency
        return self.runeinstance_set.aggregate(Avg('efficiency'))['efficiency__avg'] or 0.0

    # Stat values for current monster grade/level
    @cached_property
    def base_stats(self):
        return self.monster.get_stats(self.stars, self.level)

    @cached_property
    def max_base_stats(self):
        return self.monster.get_stats(6, 40)

    @property
    def base_hp(self):
        return self.base_stats[base.Stats.STAT_HP]

    @property
    def base_attack(self):
        return self.base_stats[base.Stats.STAT_ATK]

    @property
    def base_defense(self):
        return self.base_stats[base.Stats.STAT_DEF]

    @property
    def base_speed(self):
        return self.base_stats[base.Stats.STAT_SPD]

    @property
    def base_crit_rate(self):
        return self.base_stats[base.Stats.STAT_CRIT_RATE_PCT]

    @property
    def base_crit_damage(self):
        return self.base_stats[base.Stats.STAT_CRIT_DMG_PCT]

    @property
    def base_resistance(self):
        return self.base_stats[base.Stats.STAT_RESIST_PCT]

    @property
    def base_accuracy(self):
        return self.base_stats[base.Stats.STAT_ACCURACY_PCT]

    # Stat bonuses from default rune set
    # TODO: Use this code after switching to rune builds
    # @cached_property
    # def rune_stats(self):
    #     val = self._calc_rune_stats(self.base_stats.copy())
    #     return val
    #
    # @cached_property
    # def max_rune_stats(self):
    #     return self._calc_rune_stats(self.max_base_stats.copy())
    #
    # def _calc_rune_stats(self, base_stats):
    #     rune_stats = self.default_build.rune_stats.copy()
    #
    #     # Convert HP/ATK/DEF percentage bonuses to flat bonuses based on the base stats
    #     for stat, converts_to in base.Stats.CONVERTS_TO_FLAT_STAT.items():
    #         rune_stats[converts_to] += int(ceil(round(base_stats.get(converts_to, 0.0) * (rune_stats[stat] / 100.0), 3)))
    #         del rune_stats[stat]
    #
    #     return rune_stats
    #
    # @property
    # def rune_hp(self):
    #     val = self.rune_stats.get(base.Stats.STAT_HP, 0.0)
    #     return val
    #
    # @property
    # def rune_attack(self):
    #     return self.rune_stats.get(base.Stats.STAT_ATK, 0.0)
    #
    # @property
    # def rune_defense(self):
    #     return self.rune_stats.get(base.Stats.STAT_DEF, 0.0)
    #
    # @property
    # def rune_speed(self):
    #     return self.rune_stats.get(base.Stats.STAT_SPD, 0.0)
    #
    # @property
    # def rune_crit_rate(self):
    #     return self.rune_stats.get(base.Stats.STAT_CRIT_RATE_PCT, 0.0)
    #
    # @property
    # def rune_crit_damage(self):
    #     return self.rune_stats.get(base.Stats.STAT_CRIT_DMG_PCT, 0.0)
    #
    # @property
    # def rune_resistance(self):
    #     return self.rune_stats.get(base.Stats.STAT_RESIST_PCT, 0.0)
    #
    # @property
    # def rune_accuracy(self):
    #     return self.rune_stats.get(base.Stats.STAT_ACCURACY_PCT, 0.0)
    #
    # @property
    # def avg_rune_efficiency(self):
    #     return self.default_build.avg_efficiency

    # Totals for stats including rune bonuses
    def hp(self):
        return self.base_hp + self.rune_hp + self.artifact_hp

    def attack(self):
        return self.base_attack + self.rune_attack + self.artifact_attack

    def defense(self):
        return self.base_defense + self.rune_defense + self.artifact_defense

    def speed(self):
        return self.base_speed + self.rune_speed

    def crit_rate(self):
        return self.base_crit_rate + self.rune_crit_rate

    def crit_damage(self):
        return self.base_crit_damage + self.rune_crit_damage

    def resistance(self):
        return self.base_resistance + self.rune_resistance

    def accuracy(self):
        return self.base_accuracy + self.rune_accuracy

    def get_rune_stats(self, at_max_level=False):
        # TODO: Delete after switching to rune builds
        if at_max_level:
            base_stats = {
                RuneInstance.STAT_HP: self.monster.actual_hp(6, 40),
                RuneInstance.STAT_HP_PCT: self.monster.actual_hp(6, 40),
                RuneInstance.STAT_ATK: self.monster.actual_attack(6, 40),
                RuneInstance.STAT_ATK_PCT: self.monster.actual_attack(6, 40),
                RuneInstance.STAT_DEF: self.monster.actual_defense(6, 40),
                RuneInstance.STAT_DEF_PCT: self.monster.actual_defense(6, 40),
                RuneInstance.STAT_SPD: self.base_speed,
                RuneInstance.STAT_CRIT_RATE_PCT: self.base_crit_rate,
                RuneInstance.STAT_CRIT_DMG_PCT: self.base_crit_damage,
                RuneInstance.STAT_RESIST_PCT: self.base_resistance,
                RuneInstance.STAT_ACCURACY_PCT: self.base_accuracy,
            }
        else:
            base_stats = {
                RuneInstance.STAT_HP: self.base_hp,
                RuneInstance.STAT_HP_PCT: self.base_hp,
                RuneInstance.STAT_ATK: self.base_attack,
                RuneInstance.STAT_ATK_PCT: self.base_attack,
                RuneInstance.STAT_DEF: self.base_defense,
                RuneInstance.STAT_DEF_PCT: self.base_defense,
                RuneInstance.STAT_SPD: self.base_speed,
                RuneInstance.STAT_CRIT_RATE_PCT: self.base_crit_rate,
                RuneInstance.STAT_CRIT_DMG_PCT: self.base_crit_damage,
                RuneInstance.STAT_RESIST_PCT: self.base_resistance,
                RuneInstance.STAT_ACCURACY_PCT: self.base_accuracy,
            }

        # Update stats based on runes
        rune_set = self.runeinstance_set.all()
        stat_bonuses = {stat_id: 0 for stat_id, _ in RuneInstance.STAT_CHOICES}
        rune_set_counts = {type_id: 0 for type_id, _ in RuneInstance.TYPE_CHOICES}

        # Sum up all stat bonuses
        for rune in rune_set:
            rune_set_counts[rune.type] += 1
            stat_bonuses[RuneInstance.STAT_HP] += rune.get_stat(RuneInstance.STAT_HP)
            stat_bonuses[RuneInstance.STAT_HP_PCT] += rune.get_stat(RuneInstance.STAT_HP_PCT)
            stat_bonuses[RuneInstance.STAT_ATK] += rune.get_stat(RuneInstance.STAT_ATK)
            stat_bonuses[RuneInstance.STAT_ATK_PCT] += rune.get_stat(RuneInstance.STAT_ATK_PCT)
            stat_bonuses[RuneInstance.STAT_DEF] += rune.get_stat(RuneInstance.STAT_DEF)
            stat_bonuses[RuneInstance.STAT_DEF_PCT] += rune.get_stat(RuneInstance.STAT_DEF_PCT)
            stat_bonuses[RuneInstance.STAT_SPD] += rune.get_stat(RuneInstance.STAT_SPD)
            stat_bonuses[RuneInstance.STAT_CRIT_RATE_PCT] += rune.get_stat(RuneInstance.STAT_CRIT_RATE_PCT)
            stat_bonuses[RuneInstance.STAT_CRIT_DMG_PCT] += rune.get_stat(RuneInstance.STAT_CRIT_DMG_PCT)
            stat_bonuses[RuneInstance.STAT_RESIST_PCT] += rune.get_stat(RuneInstance.STAT_RESIST_PCT)
            stat_bonuses[RuneInstance.STAT_ACCURACY_PCT] += rune.get_stat(RuneInstance.STAT_ACCURACY_PCT)

        # Add in the set bonuses
        for set, count in rune_set_counts.items():
            required_count = RuneInstance.RUNE_SET_BONUSES[set]['count']
            bonus_value = RuneInstance.RUNE_SET_BONUSES[set]['value']
            if bonus_value is not None and count >= required_count:
                num_sets_equipped = floor(count / required_count)
                stat = RuneInstance.RUNE_SET_BONUSES[set]['stat']

                if set == RuneInstance.TYPE_SWIFT:
                    # Swift set is special because it adds a percentage to a normally flat stat
                    bonus_value = int(ceil(round(base_stats[RuneInstance.STAT_SPD] * (bonus_value / 100.0), 3)))
                    stat = RuneInstance.STAT_SPD

                stat_bonuses[stat] += bonus_value * num_sets_equipped

        # Convert HP/ATK/DEF percentage bonuses to flat bonuses based on the base stats
        for stat in [RuneInstance.STAT_HP_PCT, RuneInstance.STAT_ATK_PCT, RuneInstance.STAT_DEF_PCT]:
            stat_bonuses[stat] = int(ceil(round(base_stats[stat] * (stat_bonuses[stat] / 100.0), 3)))

        return stat_bonuses

    def get_max_level_stats(self):
        max_base_hp = self.monster.actual_hp(6, 40)
        max_base_atk = self.monster.actual_attack(6, 40)
        max_base_def = self.monster.actual_defense(6, 40)

        max_rune_stats = self.get_rune_stats(at_max_level=True)

        stats = {
            'base': {
                'hp': max_base_hp,
                'attack': max_base_atk,
                'defense': max_base_def,
            },
            'rune': {
                'hp': max_rune_stats.get(RuneInstance.STAT_HP, 0),
                'attack': max_rune_stats.get(RuneInstance.STAT_ATK, 0),
                'defense': max_rune_stats.get(RuneInstance.STAT_DEF, 0),
            },
        }

        stats['deltas'] = {
            'hp': int(round(float(stats['base']['hp'] + stats['rune']['hp']) / self.hp() * 100 - 100)),
            'attack': int(round(float(stats['base']['attack'] + stats['rune']['attack']) / self.attack() * 100 - 100)),
            'defense': int(round(float(stats['base']['defense'] + stats['rune']['defense']) / self.defense() * 100 - 100)),
        }

        return stats

    def get_building_stats(self, area=Building.AREA_GENERAL):
        owned_bldgs = BuildingInstance.objects.filter(
            Q(building__element__isnull=True) | Q(building__element=self.monster.element),
            owner=self.owner,
            building__area=area,
        ).select_related('building')

        bonuses = {
            Building.STAT_HP: 0,
            Building.STAT_ATK: 0,
            Building.STAT_DEF: 0,
            Building.STAT_SPD: 0,
            Building.STAT_CRIT_RATE_PCT: 0,
            Building.STAT_CRIT_DMG_PCT: 0,
            Building.STAT_RESIST_PCT: 0,
            Building.STAT_ACCURACY_PCT: 0,
        }

        for b in owned_bldgs:
            if b.building.affected_stat in bonuses.keys() and b.level > 0:
                bonuses[b.building.affected_stat] += b.building.stat_bonus[b.level - 1]

        return {
            'hp': int(ceil(round(self.base_hp * (bonuses[Building.STAT_HP] / 100.0), 3))),
            'attack': int(ceil(round(self.base_attack * (bonuses[Building.STAT_ATK] / 100.0), 3))),
            'defense': int(ceil(round(self.base_defense * (bonuses[Building.STAT_DEF] / 100.0), 3))),
            'speed': int(ceil(round(self.base_speed * (bonuses[Building.STAT_SPD] / 100.0), 3))),
            'crit_rate': bonuses[Building.STAT_CRIT_RATE_PCT],
            'crit_damage': bonuses[Building.STAT_CRIT_DMG_PCT],
            'resistance': bonuses[Building.STAT_RESIST_PCT],
            'accuracy': bonuses[Building.STAT_ACCURACY_PCT],
        }

    def get_guild_stats(self):
        return self.get_building_stats(Building.AREA_GUILD)

    def get_possible_skillups(self):
        same_family = Q(monster__family_id=self.monster.family_id)

        # Handle a few special cases for skillups outside of own family
        # Vampire Lord
        if self.monster.family_id == 23000:
            same_family |= Q(monster__family_id=14700)

        # Fairy Queen
        if self.monster.family_id == 19100:
            same_family |= Q(monster__family_id=10100)

        devilmon = MonsterInstance.objects.filter(owner=self.owner, monster__name='Devilmon').count()
        family = MonsterInstance.objects.filter(owner=self.owner).filter(same_family).exclude(pk=self.pk).order_by('ignore_for_fusion')
        pieces = MonsterPiece.objects.filter(owner=self.owner, monster__family_id=self.monster.family_id)

        return {
            'devilmon': devilmon,
            'family': family,
            'pieces': pieces,
            'none': devilmon + family.count() + pieces.count() == 0,
        }

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check skill levels
        if self.skill_1_level is None or self.skill_1_level < 1:
            self.skill_1_level = 1
        if self.skill_2_level is None or self.skill_2_level < 1:
            self.skill_2_level = 1
        if self.skill_3_level is None or self.skill_3_level < 1:
            self.skill_3_level = 1
        if self.skill_4_level is None or self.skill_4_level < 1:
            self.skill_4_level = 1

        if self.level > 40 or self.level < 1:
            raise ValidationError(
                'Level out of range (Valid range %(min)s-%(max)s)',
                params={'min': 1, 'max': 40},
                code='invalid_level'
            )

        if self.stars and (self.level > 10 + self.stars * 5):
            raise ValidationError(
                'Level exceeds max for given star rating (Max: %(value)s)',
                params={'value': 10 + self.stars * 5},
                code='invalid_level'
            )

        min_stars = self.monster.base_monster.base_stars

        if self.stars and (self.stars > 6 or self.stars < min_stars):
            raise ValidationError(
                'Star rating out of range (%(min)s to %(max)s)',
                params={'min': min_stars, 'max': 6},
                code='invalid_stars'
            )

        super(MonsterInstance, self).clean()

    def save(self, *args, **kwargs):
        # Remove custom name if not a homunculus
        if not self.monster.homunculus:
            self.custom_name = ''

        # Update rune stats based on level
        stat_bonuses = self.get_rune_stats()

        # Add all the bonuses together to get final values.
        self.rune_hp = stat_bonuses[RuneInstance.STAT_HP] + stat_bonuses[RuneInstance.STAT_HP_PCT]
        self.rune_attack = stat_bonuses[RuneInstance.STAT_ATK] + stat_bonuses[RuneInstance.STAT_ATK_PCT]
        self.rune_defense = stat_bonuses[RuneInstance.STAT_DEF] + stat_bonuses[RuneInstance.STAT_DEF_PCT]
        self.rune_speed = stat_bonuses[RuneInstance.STAT_SPD]
        self.rune_crit_rate = stat_bonuses[RuneInstance.STAT_CRIT_RATE_PCT]
        self.rune_crit_damage = stat_bonuses[RuneInstance.STAT_CRIT_DMG_PCT]
        self.rune_resistance = stat_bonuses[RuneInstance.STAT_RESIST_PCT]
        self.rune_accuracy = stat_bonuses[RuneInstance.STAT_ACCURACY_PCT]

        self.avg_rune_efficiency = self.get_avg_rune_efficiency()

        # save artifacts main stat bonuses
        artifacts = self.artifactinstance_set.all()
        self.artifact_hp = sum([artifact.main_stat_value for artifact in artifacts if artifact.main_stat == artifact.STAT_HP])
        self.artifact_attack = sum([artifact.main_stat_value for artifact in artifacts if artifact.main_stat == artifact.STAT_ATK])
        self.artifact_defense = sum([artifact.main_stat_value for artifact in artifacts if artifact.main_stat == artifact.STAT_DEF])

        # Limit skill levels to the max level of the skill
        skills = self.monster.skills.all()

        if len(skills) >= 1 and self.skill_1_level > skills[0].max_level:
            self.skill_1_level = skills[0].max_level

        if len(skills) >= 2 and self.skill_2_level > skills[1].max_level:
            self.skill_2_level = skills[1].max_level

        if len(skills) >= 3 and self.skill_3_level > skills[2].max_level:
            self.skill_3_level = skills[2].max_level

        if len(skills) >= 4 and self.skill_4_level > skills[3].max_level:
            self.skill_4_level = skills[3].max_level

        super(MonsterInstance, self).save(*args, **kwargs)

        if self.default_build is None or self.rta_build is None:
            self._initialize_rune_build()

    def _initialize_rune_build(self):
        # Create empty rune builds if none exists
        added = False
        if self.default_build is None:
            self.default_build = RuneBuild.objects.create(
                owner_id=self.owner.pk,
                monster_id=self.pk,
                name='Equipped Runes',
            )

        if self.rta_build is None:
            self.rta_build = RuneBuild.objects.create(
                owner_id=self.owner.pk,
                monster_id=self.pk,
                name='Real-Time Arena',
            )
            added = True

        if added:
            self.save()

        self.default_build.runes.set(self.runeinstance_set.all(), clear=True)


class MonsterPiece(models.Model):
    PIECE_REQUIREMENTS = {
        1: 10,
        2: 20,
        3: 40,
        4: 50,
        5: 100,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    pieces = models.IntegerField(default=0)

    class Meta:
        ordering = ['monster__name']

    def __str__(self):
        return str(self.monster) + ' - ' + str(self.pieces) + ' pieces'

    def can_summon(self):
        return int(floor(self.pieces / self.PIECE_REQUIREMENTS[self.monster.natural_stars]))


class RuneInstance(Rune):
    # Upgrade success rate based on rune level
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.IntegerField(choices=Rune.TYPE_CHOICES)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    com2us_id = models.BigIntegerField(blank=True, null=True)
    assigned_to = models.ForeignKey(MonsterInstance, on_delete=models.SET_NULL, blank=True, null=True)
    marked_for_sale = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    __original_assigned_to_id = None

    # Old substat fields to be removed later, but still used
    substat_1 = models.IntegerField(choices=Rune.STAT_CHOICES, null=True, blank=True)
    substat_1_value = models.IntegerField(null=True, blank=True)
    substat_1_craft = models.IntegerField(choices=RuneCraft.CRAFT_CHOICES, null=True, blank=True)
    substat_2 = models.IntegerField(choices=Rune.STAT_CHOICES, null=True, blank=True)
    substat_2_value = models.IntegerField(null=True, blank=True)
    substat_2_craft = models.IntegerField(choices=RuneCraft.CRAFT_CHOICES, null=True, blank=True)
    substat_3 = models.IntegerField(choices=Rune.STAT_CHOICES, null=True, blank=True)
    substat_3_value = models.IntegerField(null=True, blank=True)
    substat_3_craft = models.IntegerField(choices=RuneCraft.CRAFT_CHOICES, null=True, blank=True)
    substat_4 = models.IntegerField(choices=Rune.STAT_CHOICES, null=True, blank=True)
    substat_4_value = models.IntegerField(null=True, blank=True)
    substat_4_craft = models.IntegerField(choices=RuneCraft.CRAFT_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ['slot', 'type', 'level']

    def __init__(self, *args, **kwargs):
        super(RuneInstance, self).__init__(*args, **kwargs)
        self.__original_assigned_to_id = self.assigned_to_id

    def clean(self):
        super().clean()

        if self.assigned_to is not None and (self.assigned_to.runeinstance_set.filter(slot=self.slot).exclude(pk=self.pk).count() > 0):
            raise ValidationError(
                'Monster already has rune in slot %(slot)s.',
                params={
                    'slot': self.slot,
                },
                code='slot_occupied'
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.assigned_to:
            # Check no other runes are in this slot
            for rune in RuneInstance.objects.filter(assigned_to=self.assigned_to, slot=self.slot).exclude(pk=self.pk):
                rune.assigned_to = None
                rune.save()

            # Trigger stat calc update on the assigned monster
            self.assigned_to.save()

            # Update default rune build on that monster
            # TODO: Remove this once rune builds are default method of working with equipped runes
            self.assigned_to._initialize_rune_build()
        else:
            # TODO: Remove this once rune builds are default method of working with equipped runes
            if self.__original_assigned_to_id is not None and self.assigned_to is None:
                # Rune was removed, update rune build on that monster
                MonsterInstance.objects.get(pk=self.__original_assigned_to_id)._initialize_rune_build()


class RuneBuild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='')
    runes = models.ManyToManyField(RuneInstance)
    avg_efficiency = models.FloatField(default=0)
    monster = models.ForeignKey(MonsterInstance, on_delete=models.CASCADE)

    # Stat bonuses
    hp = models.IntegerField(default=0)
    hp_pct = models.IntegerField(default=0)
    attack = models.IntegerField(default=0)
    attack_pct = models.IntegerField(default=0)
    defense = models.IntegerField(default=0)
    defense_pct = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    speed_pct = models.IntegerField(default=0)
    crit_rate = models.IntegerField(default=0)
    crit_damage = models.IntegerField(default=0)
    resistance = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=0)

    # TODO: Tagging

    def __str__(self):
        return f'{self.name} - {self.rune_set_summary}'

    @cached_property
    def rune_set_summary(self):
        num_equipped = self.runes.count()

        if not num_equipped:
            return 'Empty'

        # Build list of set names
        active_set_names = [
            RuneInstance.TYPE_CHOICES[rune_type - 1][1] for rune_type in self.active_rune_sets
        ]

        # Check if broken set present
        active_set_required_count = sum([
            RuneInstance.RUNE_SET_BONUSES[rune_set]['count'] for rune_set in self.active_rune_sets
        ])

        if num_equipped > active_set_required_count:
            active_set_names.append('Broken')

        set_summary = '/'.join(active_set_names)

        # Build main stat list for even slots
        main_stat_summary = '/'.join([
            rune.get_main_stat_display() for rune in self.runes.filter(slot__in=[2, 4, 6])
        ])

        return f'{set_summary} - {main_stat_summary}'

    @cached_property
    def rune_set_bonus_text(self):
        return [
            f'{RuneInstance.RUNE_SET_BONUSES[active_set]["description"]}' for active_set in self.active_rune_sets
        ]

    @cached_property
    def active_rune_sets(self):
        completed_sets = []

        for set_counts in self.runes.values('type').order_by().annotate(count=Count('type')):
            required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[set_counts['type']]
            present = set_counts['count']
            completed_sets.extend([set_counts['type']] * (present // required))

        return completed_sets

    @cached_property
    def rune_stats(self):
        stats = {
            base.Stats.STAT_HP: self.hp,
            base.Stats.STAT_HP_PCT: self.hp_pct,
            base.Stats.STAT_ATK: self.attack,
            base.Stats.STAT_ATK_PCT: self.attack_pct,
            base.Stats.STAT_DEF: self.defense,
            base.Stats.STAT_DEF_PCT: self.defense_pct,
            base.Stats.STAT_SPD: self.speed,
            base.Stats.STAT_CRIT_RATE_PCT: self.crit_rate,
            base.Stats.STAT_CRIT_DMG_PCT: self.crit_damage,
            base.Stats.STAT_RESIST_PCT: self.resistance,
            base.Stats.STAT_ACCURACY_PCT: self.accuracy,
        }

        return stats

    def update_stats(self):
        # Sum all stats on the runes
        stat_bonuses = {}
        runes = self.runes.all()
        for stat, _ in RuneInstance.STAT_CHOICES:
            if stat not in stat_bonuses:
                stat_bonuses[stat] = 0

            for rune in runes:
                stat_bonuses[stat] += rune.get_stat(stat)

        # Add in any active set bonuses
        stat_bonuses[RuneInstance.STAT_SPD_PCT] = 0
        for active_set in self.active_rune_sets:
            stat = RuneInstance.RUNE_SET_BONUSES[active_set]['stat']
            if stat:
                stat_bonuses[stat] += RuneInstance.RUNE_SET_BONUSES[active_set]['value']

        self.hp = stat_bonuses.get(base.Stats.STAT_HP, 0)
        self.hp_pct = stat_bonuses.get(base.Stats.STAT_HP_PCT, 0)
        self.attack = stat_bonuses.get(base.Stats.STAT_ATK, 0)
        self.attack_pct = stat_bonuses.get(base.Stats.STAT_ATK_PCT, 0)
        self.defense = stat_bonuses.get(base.Stats.STAT_DEF, 0)
        self.defense_pct = stat_bonuses.get(base.Stats.STAT_DEF_PCT, 0)
        self.speed = stat_bonuses.get(base.Stats.STAT_SPD, 0)
        self.speed_pct = stat_bonuses.get(base.Stats.STAT_SPD_PCT, 0)
        self.crit_rate = stat_bonuses.get(base.Stats.STAT_CRIT_RATE_PCT, 0)
        self.crit_damage = stat_bonuses.get(base.Stats.STAT_CRIT_DMG_PCT, 0)
        self.resistance = stat_bonuses.get(base.Stats.STAT_RESIST_PCT, 0)
        self.accuracy = stat_bonuses.get(base.Stats.STAT_ACCURACY_PCT, 0)
        self.avg_efficiency = self.runes.aggregate(Avg('efficiency'))['efficiency__avg'] or 0.0


class RuneCraftInstance(RuneCraft):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    com2us_id = models.BigIntegerField(blank=True, null=True)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['type', 'rune']

    def clean(self):
        super().clean()

        if self.quantity < 1:
            raise ValidationError({'quantity': ValidationError(
                'Quantity must be 1 or more',
                code='invalid_quantity'
            )})


class ArtifactInstance(Artifact):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    com2us_id = models.BigIntegerField(blank=True, null=True)
    assigned_to = models.ForeignKey(MonsterInstance, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.assigned_to:
            # Check no other artifacts are in this slot
            for artifact in ArtifactInstance.objects.filter(assigned_to=self.assigned_to, slot=self.slot).exclude(pk=self.pk):
                artifact.assigned_to = None
                artifact.save()

            # Trigger stat calc update on the assigned monster
            self.assigned_to.save()


class ArtifactCraftInstance(ArtifactCraft):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    com2us_id = models.BigIntegerField(blank=True, null=True)
    quantity = models.IntegerField(default=1)


class TeamGroup(models.Model):
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(TeamGroup, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30)
    favorite = models.BooleanField(default=False, blank=True)
    description = models.TextField(
        null=True,
        blank=True,
        help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled')
    )
    leader = models.ForeignKey('MonsterInstance', on_delete=models.SET_NULL, related_name='team_leader', null=True, blank=True)
    roster = models.ManyToManyField('MonsterInstance', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BuildingInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    level = models.IntegerField()

    class Meta:
        ordering = ['building']

    def remaining_upgrade_cost(self):
        return sum(self.building.upgrade_cost[self.level:])

    def __str__(self):
        return str(self.building) + ', Lv.' + str(self.level)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.level and self.building and (self.level < 0 or self.level > self.building.max_level):
            raise ValidationError({
                    'level': ValidationError(
                        'Level must be between %s and %s' % (0, self.building.max_level),
                        code='invalid_level',
                    )
                })

    def update_fields(self):
        self.level = min(max(0, self.level), self.building.max_level)

    def save(self, *args, **kwargs):
        self.update_fields()
        super(BuildingInstance, self).save(*args, **kwargs)
