import uuid
from collections import OrderedDict
from math import floor, ceil

from django.core.exceptions import MultipleObjectsReturned
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
    server = models.IntegerField(
        choices=SERVER_CHOICES, default=SERVER_GLOBAL, null=True, blank=True)
    following = models.ManyToManyField(
        "self", related_name='followed_by', symmetrical=False)
    public = models.BooleanField(default=False, blank=True)
    dark_mode = models.BooleanField(default=False, blank=True)
    timezone = TimeZoneField(default='America/Los_Angeles')
    notes = models.TextField(null=True, blank=True)
    preferences = JSONField(default=dict, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    consent_report = models.BooleanField(null=True, blank=True)
    consent_top = models.BooleanField(null=True, blank=True)

    def has_given_consent(self):
        return self.consent_report is not None and self.consent_top is not None

    def get_rune_counts(self):
        counts = {}

        for rune_type in RuneInstance.TYPE_CHOICES:
            counts[rune_type[1]] = RuneInstance.objects.filter(
                owner=self, type=rune_type[0]).count()

        return counts

    def save(self, *args, **kwargs):
        super(Summoner, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Storage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    @staticmethod
    def _min_zero(x):
        return max(x, 0)

    def save(self, *args, **kwargs):
        self.quantity = self._min_zero(self.quantity)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class MaterialStorage(Storage):
    item = models.ForeignKey(GameItem, on_delete=models.CASCADE)

    class Meta:
        ordering = ['item']
        unique_together = [['owner', 'item']]


class MonsterShrineStorage(Storage):
    item = models.ForeignKey(Monster, on_delete=models.CASCADE)

    class Meta:
        ordering = ['item']
        unique_together = [['owner', 'item']]


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
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES, blank=True, null=True)
    tags = models.ManyToManyField(MonsterTag, blank=True)
    notes = models.TextField(null=True, blank=True, help_text=mark_safe(
        '<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    custom_name = models.CharField(default='', max_length=20, blank=True)
    default_build = models.ForeignKey(
        'RuneBuild', null=True, on_delete=models.SET_NULL, related_name='default_build')
    rta_build = models.ForeignKey(
        'RuneBuild', null=True, on_delete=models.SET_NULL, related_name='rta_build')

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
        skill_levels = [self.skill_1_level, self.skill_2_level,
                        self.skill_3_level, self.skill_4_level]

        for idx in range(0, self.monster.skills.count()):
            skill_ups_remaining -= skill_levels[idx] - 1

        return skill_ups_remaining

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
    @cached_property
    def rune_stats(self):
        val = self._calc_rune_stats(self.base_stats.copy())
        return val
    
    @cached_property
    def max_rune_stats(self):
        return self._calc_rune_stats(self.max_base_stats.copy())
    
    def _calc_rune_stats(self, base_stats):
        if not self.default_build or not self.rta_build:
            self._initialize_rune_build()
        rune_stats = self.default_build.rune_stats.copy()
    
        # Convert HP/ATK/DEF percentage bonuses to flat bonuses based on the base stats
        for stat, converts_to in base.Stats.CONVERTS_TO_FLAT_STAT.items():
            rune_stats[converts_to] += int(ceil(round(base_stats.get(converts_to, 0.0) * (rune_stats[stat] / 100.0), 3)))
            del rune_stats[stat]
    
        return rune_stats
    
    @property
    def rune_hp(self):
        val = self.rune_stats.get(base.Stats.STAT_HP, 0.0)
        return val
    
    @property
    def rune_attack(self):
        return self.rune_stats.get(base.Stats.STAT_ATK, 0.0)
    
    @property
    def rune_defense(self):
        return self.rune_stats.get(base.Stats.STAT_DEF, 0.0)
    
    @property
    def rune_speed(self):
        return self.rune_stats.get(base.Stats.STAT_SPD, 0.0)
    
    @property
    def rune_crit_rate(self):
        return self.rune_stats.get(base.Stats.STAT_CRIT_RATE_PCT, 0.0)
    
    @property
    def rune_crit_damage(self):
        return self.rune_stats.get(base.Stats.STAT_CRIT_DMG_PCT, 0.0)
    
    @property
    def rune_resistance(self):
        return self.rune_stats.get(base.Stats.STAT_RESIST_PCT, 0.0)
    
    @property
    def rune_accuracy(self):
        return self.rune_stats.get(base.Stats.STAT_ACCURACY_PCT, 0.0)

    # Totals for stats including rune bonuses
    def hp(self):
        return self.base_hp + self.rune_hp

    def attack(self):
        return self.base_attack + self.rune_attack

    def defense(self):
        return self.base_defense + self.rune_defense

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

    def effective_hp(self):
        return int(ceil(self.hp() * (1140 + self.defense() * 3.5) / 1000))

    def efficiency(self):
        return self.default_build.avg_efficiency

    def get_max_level_stats(self):
        stats = {
            'base': {
                'hp': self.monster.actual_hp(6, 40),
                'attack': self.monster.actual_attack(6, 40),
                'defense': self.monster.actual_defense(6, 40),
            },
            'rune': {
                'hp': self.max_rune_stats.get(RuneInstance.STAT_HP, 0) + self.max_rune_stats.get(RuneInstance.STAT_HP_PCT, 0),
                'attack': self.max_rune_stats.get(RuneInstance.STAT_ATK, 0) + self.max_rune_stats.get(RuneInstance.STAT_ATK_PCT, 0),
                'defense': self.max_rune_stats.get(RuneInstance.STAT_DEF, 0) + self.max_rune_stats.get(RuneInstance.STAT_DEF_PCT, 0),
            },
        }

        stats['deltas'] = {
            'hp': int(round(float(stats['base']['hp'] + stats['rune']['hp']) / self.hp() * 100 - 100)),
            'attack': int(round(float(stats['base']['attack'] + stats['rune']['attack']) / self.attack() * 100 - 100)),
            'defense': int(round(float(stats['base']['defense'] + stats['rune']['defense']) / self.defense() * 100 - 100)),
        }

        stats['rune']['effective_hp'] = int(ceil(float(stats['base']['hp'] + stats['rune']['hp']) * (1140 + (float(stats['base']['defense'] + stats['rune']['defense'])) * 3.5) / 1000))
        stats['deltas']['effective_hp'] = int(round(stats['rune']['effective_hp'] / self.effective_hp() * 100 - 100))

        return stats

    def get_building_stats(self, area=Building.AREA_GENERAL):
        owned_bldgs = BuildingInstance.objects.filter(
            Q(building__element__isnull=True) | Q(
                building__element=self.monster.element),
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

        building_stats = {
            'hp': int(ceil(round(self.base_hp * (bonuses[Building.STAT_HP] / 100.0), 3))),
            'attack': int(ceil(round(self.base_attack * (bonuses[Building.STAT_ATK] / 100.0), 3))),
            'defense': int(ceil(round(self.base_defense * (bonuses[Building.STAT_DEF] / 100.0), 3))),
            'speed': int(ceil(round(self.base_speed * (bonuses[Building.STAT_SPD] / 100.0), 3))),
            'crit_rate': bonuses[Building.STAT_CRIT_RATE_PCT],
            'crit_damage': bonuses[Building.STAT_CRIT_DMG_PCT],
            'resistance': bonuses[Building.STAT_RESIST_PCT],
            'accuracy': bonuses[Building.STAT_ACCURACY_PCT],
        }

        building_stats['effective_hp'] = int(ceil((self.hp() + building_stats['hp']) * (1140 + 3.5 * (self.defense() + building_stats['defense'])) / 1000)) - self.effective_hp()

        return building_stats

    def get_guild_stats(self):
        return self.get_building_stats(Building.AREA_GUILD)

    def get_possible_skillups(self):
        same_skill_group = Q(
            monster__skill_group_id=self.monster.skill_group_id)
        same_skill_group_shrine = Q(
            item__skill_group_id=self.monster.skill_group_id)

        devilmon = MonsterInstance.objects.filter(
            owner=self.owner, monster__name='Devilmon').count()
        skill_group = MonsterInstance.objects.filter(owner=self.owner).filter(
            same_skill_group).exclude(pk=self.pk).order_by('ignore_for_fusion')
        pieces = MonsterPiece.objects.filter(
            owner=self.owner, monster__skill_group_id=self.monster.skill_group_id)

        try:
            devilmon_material_storage = MaterialStorage.objects.select_related(
                'item').get(owner=self.owner, item__name__icontains='devilmon')
            devilmon += devilmon_material_storage.quantity
        except MaterialStorage.DoesNotExist:
            pass
        except MultipleObjectsReturned:
            # should be better handling for this
            pass

        family_shrine = sum([m.quantity for m in MonsterShrineStorage.objects.filter(owner=self.owner).filter(same_skill_group_shrine)])

        return {
            'devilmon': devilmon,
            'skill_group': skill_group,
            'pieces': pieces,
            'family_shrine': family_shrine,
            'none': devilmon + skill_group.count() + pieces.count() + family_shrine == 0,
        }

    def clean(self):
        super().clean()

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

        min_stars = self.monster.base_monster.natural_stars

        if self.stars and (self.stars > 6 or self.stars < min_stars):
            raise ValidationError(
                'Star rating out of range (%(min)s to %(max)s)',
                params={'min': min_stars, 'max': 6},
                code='invalid_stars'
            )

    def save(self, *args, **kwargs):
        # Remove custom name if not a homunculus
        if not self.monster.homunculus:
            self.custom_name = ''

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
            self.save()

    def _initialize_rune_build(self):
        # Create empty rune builds if none exists
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
        unique_together = [['owner', 'monster']]

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
    assigned_to = models.ForeignKey(
        MonsterInstance, on_delete=models.SET_NULL, blank=True, null=True, related_name='runes')
    rta_assigned_to = models.ForeignKey(
        MonsterInstance, on_delete=models.SET_NULL, blank=True, null=True, related_name='runes_rta')
    marked_for_sale = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['slot', 'type', 'level']


class RuneBuild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='')
    runes = models.ManyToManyField(RuneInstance)
    artifacts = models.ManyToManyField('ArtifactInstance')
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

    def __str__(self):
        return f'{self.name} - {self.rune_set_summary}'

    @cached_property
    def rune_set_text(self):
        main_stat_text = self.rune_set_summary.find(' - ')
        if main_stat_text > -1:
            return self.rune_set_summary[:main_stat_text]
        return self.rune_set_summary

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

        set_summary = ' / '.join(active_set_names)

        # Build main stat list for even slots
        main_stat_summary = ' / '.join([
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
        missing_one = []
        has_intangible = self.runes.filter(type=RuneInstance.TYPE_INTANGIBLE).exists()

        for set_counts in self.runes.exclude(type=RuneInstance.TYPE_INTANGIBLE).values('type').order_by().annotate(count=Count('type')):
            required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[set_counts['type']]
            present = set_counts['count']
            completed_sets.extend([set_counts['type']] * (present // required))
            if has_intangible and present % required == 1:
                missing_one.append(set_counts['type'])
        
        if len(missing_one) == 1:
            missing_set = missing_one[0]
            last_set_occur = completed_sets[::-1].index(missing_set)
            if last_set_occur > -1:
                proper_index = len(completed_sets) - last_set_occur
                completed_sets[proper_index:proper_index] = missing_one

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
            base.Stats.STAT_SPD_PCT: self.speed_pct,
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
        artifacts = self.artifacts.all()

        for stat, _ in RuneInstance.STAT_CHOICES:
            if stat not in stat_bonuses:
                stat_bonuses[stat] = 0

            for rune in runes:
                stat_bonuses[stat] += rune.get_stat(stat)

        for artifact in artifacts:
            # artifact has only main stat, which increases base monster stats
            stat_bonuses[artifact.main_stat] += artifact.main_stat_value

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
        self.avg_efficiency = self.runes.aggregate(
            Avg('efficiency'))['efficiency__avg'] or 0.0

    def clear_cache_properties(self):
        fields = [
            "rune_set_text",
            "rune_set_summary",
            "rune_set_bonus_text",
            "active_rune_sets",
            "rune_stats",
            "runes_per_slot",
            "artifacts_per_slot",
        ]

        for field in fields: 
            try:
                delattr(self, field)
            except AttributeError:
                pass 

    def assign_rune(self, rune):
        # Clear any existing rune in slot
        self.runes.remove(*self.runes.filter(slot=rune.slot))
        self.runes.add(rune)

    def assign_artifact(self, artifact):
        # Clear any existing artifact in slot
        self.artifacts.remove(*self.artifacts.filter(slot=artifact.slot))
        self.artifacts.add(artifact)

    @cached_property
    def runes_per_slot(self):
        runes = OrderedDict([(i, None) for i in range(1, 7)])
        for rune in self.runes.all():
            runes[rune.slot] = rune

        return runes

    @cached_property
    def artifacts_per_slot(self):
        artifacts = OrderedDict([(desc.lower(), None) for _, desc in ArtifactInstance.SLOT_CHOICES])

        for artifact in self.artifacts.all():
            artifacts[artifact.get_slot_display().lower()] = artifact

        return artifacts

    def get_artifact_element(self):
        return self.artifacts_per_slot[Artifact.SLOT_ELEMENTAL]

    def get_artifact_archetype(self):
        return self.artifacts_per_slot[Artifact.SLOT_ARCHETYPE]


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
    assigned_to = models.ForeignKey(
        MonsterInstance, on_delete=models.SET_NULL, blank=True, null=True, related_name='artifacts')
    rta_assigned_to = models.ForeignKey(
        MonsterInstance, on_delete=models.SET_NULL, blank=True, null=True, related_name='artifacts_rta')


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
    owner = models.ForeignKey(
        Summoner, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey(
        Level, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(TeamGroup, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30)
    favorite = models.BooleanField(default=False, blank=True)
    description = models.TextField(
        null=True,
        blank=True,
        help_text=mark_safe(
            '<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled')
    )
    leader = models.ForeignKey('MonsterInstance', on_delete=models.SET_NULL,
                               related_name='team_leader', null=True, blank=True)
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
                    'Level must be between %s and %s' % (
                        0, self.building.max_level),
                    code='invalid_level',
                )
            })

    def update_fields(self):
        self.level = min(max(0, self.level), self.building.max_level)

    def save(self, *args, **kwargs):
        self.update_fields()
        super(BuildingInstance, self).save(*args, **kwargs)
