import uuid
from collections import OrderedDict
from math import floor, ceil

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Count
from django.utils.safestring import mark_safe
from timezone_field import TimeZoneField

from bestiary.models import Monster, Building, Level, Rune, RuneCraft


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
    preferences = JSONField(default=dict)
    last_update = models.DateTimeField(auto_now=True)

    def get_rune_counts(self):
        counts = {}

        for rune_type in RuneInstance.TYPE_CHOICES:
            counts[rune_type[1]] = RuneInstance.objects.filter(owner=self, type=rune_type[0]).count()

        return counts

    def save(self, *args, **kwargs):
        super(Summoner, self).save(*args, **kwargs)

        # Update new storage model
        if not hasattr(self, 'storage'):
            new_storage = Storage.objects.create(
                owner=self,
            )
            new_storage.save()

    def __str__(self):
        return self.user.username


def _default_storage_data():
    return [0, 0, 0]


class Storage(models.Model):
    ESSENCE_LOW = 0
    ESSENCE_MID = 1
    ESSENCE_HIGH = 2

    ESSENCE_SIZES = [
        (ESSENCE_LOW, 'Low'),
        (ESSENCE_MID, 'Mid'),
        (ESSENCE_HIGH, 'High'),
    ]

    ESSENCE_FIELDS = ['magic_essence', 'fire_essence', 'water_essence', 'wind_essence', 'light_essence', 'dark_essence']
    CRAFT_FIELDS = [
        'wood',
        'leather',
        'rock',
        'ore',
        'mithril',
        'cloth',
        'rune_piece',
        'dust',
        'symbol_harmony',
        'symbol_transcendance',
        'symbol_chaos',
        'crystal_water',
        'crystal_fire',
        'crystal_wind',
        'crystal_light',
        'crystal_dark',
        'crystal_magic',
        'crystal_pure',
    ]
    MONSTER_FIELDS = [
        'fire_angelmon',
        'water_angelmon',
        'wind_angelmon',
        'light_angelmon',
        'dark_angelmon',
        'fire_king_angelmon',
        'water_king_angelmon',
        'wind_king_angelmon',
        'light_king_angelmon',
        'dark_king_angelmon',
        'rainbowmon_2_20',
        'rainbowmon_3_1',
        'rainbowmon_3_25',
        'rainbowmon_4_1',
        'rainbowmon_4_30',
        'rainbowmon_5_1',
        'super_angelmon',
        'devilmon',
    ]

    owner = models.OneToOneField(Summoner, on_delete=models.CASCADE)

    # Elemental Essences
    magic_essence = ArrayField(models.IntegerField(default=0), size=3, default=_default_storage_data, help_text='Magic Essence')
    fire_essence = ArrayField(models.IntegerField(default=0), size=3, default=_default_storage_data, help_text='Fire Essence')
    water_essence = ArrayField(models.IntegerField(default=0), size=3, default=_default_storage_data, help_text='Water Essence')
    wind_essence = ArrayField(models.IntegerField(default=0), size=3, default=_default_storage_data, help_text='Wind Essence')
    light_essence = ArrayField(models.IntegerField(default=0), size=3, default=_default_storage_data, help_text='Light Essence')
    dark_essence = ArrayField(models.IntegerField(default=0), size=3, default=_default_storage_data, help_text='Dark Essence')

    # Crafting materials
    wood = models.IntegerField(default=0, help_text='Hard Wood')
    leather = models.IntegerField(default=0, help_text='Tough Leather')
    rock = models.IntegerField(default=0, help_text='Solid Rock')
    ore = models.IntegerField(default=0, help_text='Solid Iron Ore')
    mithril = models.IntegerField(default=0, help_text='Shining Mythril')
    cloth = models.IntegerField(default=0, help_text='Thick Cloth')
    rune_piece = models.IntegerField(default=0, help_text='Rune Piece')
    dust = models.IntegerField(default=0, help_text='Magic Dust')
    symbol_harmony = models.IntegerField(default=0, help_text='Symbol of Harmony')
    symbol_transcendance = models.IntegerField(default=0, help_text='Symbol of Transcendance')
    symbol_chaos = models.IntegerField(default=0, help_text='Symbol of Chaos')
    crystal_water = models.IntegerField(default=0, help_text='Frozen Water Crystal')
    crystal_fire = models.IntegerField(default=0, help_text='Flaming Fire Crystal')
    crystal_wind = models.IntegerField(default=0, help_text='Whirling Wind Crystal')
    crystal_light = models.IntegerField(default=0, help_text='Shiny Light Crystal')
    crystal_dark = models.IntegerField(default=0, help_text='Pitch-black Dark Crystal')
    crystal_magic = models.IntegerField(default=0, help_text='Condensed Magic Crystal')
    crystal_pure = models.IntegerField(default=0, help_text='Pure Magic Crystal')

    # Material monsters
    fire_angelmon = models.IntegerField(default=0, help_text='Fire Angelmon')
    water_angelmon = models.IntegerField(default=0, help_text='Water Angelmon')
    wind_angelmon = models.IntegerField(default=0, help_text='Wind Angelmon')
    light_angelmon = models.IntegerField(default=0, help_text='Light Angelmon')
    dark_angelmon = models.IntegerField(default=0, help_text='Dark Angelmon')

    fire_king_angelmon = models.IntegerField(default=0, help_text='Fire King Angelmon')
    water_king_angelmon = models.IntegerField(default=0, help_text='Water King Angelmon')
    wind_king_angelmon = models.IntegerField(default=0, help_text='Wind King Angelmon')
    light_king_angelmon = models.IntegerField(default=0, help_text='Light King Angelmon')
    dark_king_angelmon = models.IntegerField(default=0, help_text='Dark King Angelmon')

    super_angelmon = models.IntegerField(default=0, help_text='Super Angelmon')
    devilmon = models.IntegerField(default=0, help_text='Devilmon')

    rainbowmon_2_20 = models.IntegerField(default=0, help_text='Rainbowmon 2⭐ lv.20')
    rainbowmon_3_1 = models.IntegerField(default=0, help_text='Rainbowmon 3⭐ lv.1')
    rainbowmon_3_25 = models.IntegerField(default=0, help_text='Rainbowmon 3⭐ lv.25')
    rainbowmon_4_1 = models.IntegerField(default=0, help_text='Rainbowmon 4⭐ lv.1')
    rainbowmon_4_30 = models.IntegerField(default=0, help_text='Rainbowmon 4⭐ lv.30')
    rainbowmon_5_1 = models.IntegerField(default=0, help_text='Rainbowmon 5⭐ lv.1')

    def get_storage(self):
        storage = OrderedDict()
        storage['magic'] = OrderedDict()
        storage['magic']['low'] = self.magic_essence[Storage.ESSENCE_LOW]
        storage['magic']['mid'] = self.magic_essence[Storage.ESSENCE_MID]
        storage['magic']['high'] = self.magic_essence[Storage.ESSENCE_HIGH]
        storage['fire'] = OrderedDict()
        storage['fire']['low'] = self.fire_essence[Storage.ESSENCE_LOW]
        storage['fire']['mid'] = self.fire_essence[Storage.ESSENCE_MID]
        storage['fire']['high'] = self.fire_essence[Storage.ESSENCE_HIGH]
        storage['water'] = OrderedDict()
        storage['water']['low'] = self.water_essence[Storage.ESSENCE_LOW]
        storage['water']['mid'] = self.water_essence[Storage.ESSENCE_MID]
        storage['water']['high'] = self.water_essence[Storage.ESSENCE_HIGH]
        storage['wind'] = OrderedDict()
        storage['wind']['low'] = self.wind_essence[Storage.ESSENCE_LOW]
        storage['wind']['mid'] = self.wind_essence[Storage.ESSENCE_MID]
        storage['wind']['high'] = self.wind_essence[Storage.ESSENCE_HIGH]
        storage['light'] = OrderedDict()
        storage['light']['low'] = self.light_essence[Storage.ESSENCE_LOW]
        storage['light']['mid'] = self.light_essence[Storage.ESSENCE_MID]
        storage['light']['high'] = self.light_essence[Storage.ESSENCE_HIGH]
        storage['dark'] = OrderedDict()
        storage['dark']['low'] = self.dark_essence[Storage.ESSENCE_LOW]
        storage['dark']['mid'] = self.dark_essence[Storage.ESSENCE_MID]
        storage['dark']['high'] = self.dark_essence[Storage.ESSENCE_HIGH]

        return storage

    @staticmethod
    def _min_zero(x):
        return max(x, 0)

    def save(self, *args, **kwargs):
        # Ensure all are at 0 or higher
        self.magic_essence = list(map(self._min_zero, self.magic_essence))
        self.fire_essence = list(map(self._min_zero, self.fire_essence))
        self.wind_essence = list(map(self._min_zero, self.wind_essence))
        self.light_essence = list(map(self._min_zero, self.light_essence))
        self.dark_essence = list(map(self._min_zero, self.dark_essence))

        self.wood = max(self.wood, 0)
        self.leather = max(self.leather, 0)
        self.rock = max(self.rock, 0)
        self.ore = max(self.ore, 0)
        self.mithril = max(self.mithril, 0)
        self.cloth = max(self.cloth, 0)
        self.rune_piece = max(self.rune_piece, 0)
        self.dust = max(self.dust, 0)
        self.symbol_harmony = max(self.symbol_harmony, 0)
        self.symbol_transcendance = max(self.symbol_transcendance, 0)
        self.symbol_chaos = max(self.symbol_chaos, 0)
        self.crystal_water = max(self.crystal_water, 0)
        self.crystal_fire = max(self.crystal_fire, 0)
        self.crystal_wind = max(self.crystal_wind, 0)
        self.crystal_light = max(self.crystal_light, 0)
        self.crystal_dark = max(self.crystal_dark, 0)
        self.crystal_magic = max(self.crystal_magic, 0)
        self.crystal_pure = max(self.crystal_pure, 0)

        super(Storage, self).save(*args, **kwargs)


class MonsterTag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return mark_safe(self.name)


class MonsterInstance(models.Model):
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
    stars = models.IntegerField()
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

    # Calculated fields (on save)
    base_hp = models.IntegerField(blank=True, default=0)
    rune_hp = models.IntegerField(blank=True, default=0)
    base_attack = models.IntegerField(blank=True, default=0)
    rune_attack = models.IntegerField(blank=True, default=0)
    base_defense = models.IntegerField(blank=True, default=0)
    rune_defense = models.IntegerField(blank=True, default=0)
    base_speed = models.IntegerField(blank=True, default=0)
    rune_speed = models.IntegerField(blank=True, default=0)
    base_crit_rate = models.IntegerField(blank=True, default=0)
    rune_crit_rate = models.IntegerField(blank=True, default=0)
    base_crit_damage = models.IntegerField(blank=True, default=0)
    rune_crit_damage = models.IntegerField(blank=True, default=0)
    base_resistance = models.IntegerField(blank=True, default=0)
    rune_resistance = models.IntegerField(blank=True, default=0)
    base_accuracy = models.IntegerField(blank=True, default=0)
    rune_accuracy = models.IntegerField(blank=True, default=0)
    avg_rune_efficiency = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['-stars', '-level', 'monster__name']

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
            type_name = RuneInstance.TYPE_CHOICES[rune_count['type'] - 1][1]
            required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[rune_count['type']]
            present = rune_count['count']
            bonus_text = RuneInstance.RUNE_SET_BONUSES[rune_count['type']]['description']

            if present >= required:
                rune_bonuses.extend([type_name + ' ' + bonus_text] * (present // required))

        return rune_bonuses

    def get_avg_rune_efficiency(self):
        efficiencies = sum(self.runeinstance_set.filter(efficiency__isnull=False).values_list('efficiency', flat=True))
        return efficiencies / 6

    # Stat callables. Base = monster's own stat. Rune = amount gained from runes. Stat by itself is combined total
    def calc_base_hp(self):
        return self.monster.actual_hp(self.stars, self.level)

    def hp(self):
        return self.base_hp + self.rune_hp

    def calc_base_attack(self):
        return self.monster.actual_attack(self.stars, self.level)

    def attack(self):
        return self.base_attack + self.rune_attack

    def calc_base_defense(self):
        return self.monster.actual_defense(self.stars, self.level)

    def defense(self):
        return self.base_defense + self.rune_defense

    def calc_base_speed(self):
        return self.monster.speed

    def speed(self):
        return self.base_speed + self.rune_speed

    def calc_base_crit_rate(self):
        return self.monster.crit_rate

    def crit_rate(self):
        return self.base_crit_rate + self.rune_crit_rate

    def calc_base_crit_damage(self):
        return self.monster.crit_damage

    def crit_damage(self):
        return self.base_crit_damage + self.rune_crit_damage

    def calc_base_resistance(self):
        return self.monster.resistance

    def resistance(self):
        return self.base_resistance + self.rune_resistance

    def calc_base_accuracy(self):
        return self.monster.accuracy

    def accuracy(self):
        return self.base_accuracy + self.rune_accuracy

    def get_base_stats(self):
        return {
            RuneInstance.STAT_HP: self.base_hp,
            RuneInstance.STAT_HP_PCT: self.base_hp,
            RuneInstance.STAT_DEF: self.base_defense,
            RuneInstance.STAT_DEF_PCT: self.base_defense,
            RuneInstance.STAT_SPD: self.base_speed,
            RuneInstance.STAT_CRIT_RATE_PCT: self.base_crit_rate,
            RuneInstance.STAT_CRIT_DMG_PCT: self.base_crit_damage,
            RuneInstance.STAT_RESIST_PCT: self.base_resistance,
            RuneInstance.STAT_ACCURACY_PCT: self.base_accuracy,
        }

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
                'hp': max_rune_stats[RuneInstance.STAT_HP] + max_rune_stats[RuneInstance.STAT_HP_PCT],
                'attack': max_rune_stats[RuneInstance.STAT_ATK] + max_rune_stats[RuneInstance.STAT_ATK_PCT],
                'defense': max_rune_stats[RuneInstance.STAT_DEF] + max_rune_stats[RuneInstance.STAT_DEF_PCT],
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
        devilmon = MonsterInstance.objects.filter(owner=self.owner, monster__name='Devilmon').count()
        family = MonsterInstance.objects.filter(owner=self.owner, monster__family_id=self.monster.family_id).exclude(pk=self.pk).order_by('ignore_for_fusion')
        pieces = MonsterPiece.objects.filter(owner=self.owner, monster__family_id=self.monster.family_id)

        return {
            'devilmon': devilmon,
            'family': family,
            'pieces': pieces,
            'none': devilmon + family.count() + pieces.count() == 0,
        }

    def get_rune_stats(self, at_max_level=False):
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

                stat_bonuses[stat] += bonus_value * num_sets_equipped

        # Convert HP/ATK/DEF percentage bonuses to flat bonuses based on the base stats
        for stat in [RuneInstance.STAT_HP_PCT, RuneInstance.STAT_ATK_PCT, RuneInstance.STAT_DEF_PCT]:
            stat_bonuses[stat] = int(ceil(round(base_stats[stat] * (stat_bonuses[stat] / 100.0), 3)))

        return stat_bonuses

    def update_fields(self):
        # Remove custom name if not a homunculus
        if not self.monster.homunculus:
            self.custom_name = ''

        # Update base stats based on level
        self.base_hp = self.calc_base_hp()
        self.base_attack = self.calc_base_attack()
        self.base_defense = self.calc_base_defense()
        self.base_speed = self.calc_base_speed()
        self.base_crit_rate = self.calc_base_crit_rate()
        self.base_crit_damage = self.calc_base_crit_damage()
        self.base_resistance = self.calc_base_resistance()
        self.base_accuracy = self.calc_base_accuracy()

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

    def clean(self):
        from django.core.exceptions import ValidationError, ObjectDoesNotExist

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

        try:
            min_stars = self.monster.base_stars
            if self.monster.is_awakened:
                min_stars -= 1
        except ObjectDoesNotExist:
            min_stars = 1

        if self.stars and (self.stars > 6 or self.stars < min_stars):
            raise ValidationError(
                'Star rating out of range (%(min)s to %(max)s)',
                params={'min': min_stars, 'max': 6},
                code='invalid_stars'
            )

        super(MonsterInstance, self).clean()

    def save(self, *args, **kwargs):
        self.update_fields()
        super(MonsterInstance, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.monster) + ', ' + str(self.stars) + '*, Lvl ' + str(self.level)


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

    substats_enchanted = ArrayField(
        models.BooleanField(default=False, blank=True),
        size=4,
        default=list,
    )
    substats_grind_value = ArrayField(
        models.IntegerField(default=0, blank=True),
        size=4,
        default=list,
    )

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

    def get_substat_1_rune_display(self):
        return self.get_substat_rune_display(0)

    def get_substat_2_rune_display(self):
        return self.get_substat_rune_display(1)

    def get_substat_3_rune_display(self):
        return self.get_substat_rune_display(2)

    def get_substat_4_rune_display(self):
        return self.get_substat_rune_display(3)

    def get_stat(self, stat_type, sub_stats_only=False):
        if self.main_stat == stat_type and not sub_stats_only:
            return self.main_stat_value
        elif self.innate_stat == stat_type and not sub_stats_only:
            return self.innate_stat_value
        else:
            for idx, substat in enumerate(self.substats):
                if substat == stat_type:
                    return self.substat_values[idx] + self.substats_grind_value[idx]

        # Nothing matching queried stat type
        return 0

    # Individual functions for each stat to use within templates
    def get_hp_pct(self):
        return self.get_stat(RuneInstance.STAT_HP_PCT, False)

    def get_hp(self):
        return self.get_stat(RuneInstance.STAT_HP, False)

    def get_def_pct(self):
        return self.get_stat(RuneInstance.STAT_DEF_PCT, False)

    def get_def(self):
        return self.get_stat(RuneInstance.STAT_DEF, False)

    def get_atk_pct(self):
        return self.get_stat(RuneInstance.STAT_ATK_PCT, False)

    def get_atk(self):
        return self.get_stat(RuneInstance.STAT_ATK, False)

    def get_spd(self):
        return self.get_stat(RuneInstance.STAT_SPD, False)

    def get_cri_rate(self):
        return self.get_stat(RuneInstance.STAT_CRIT_RATE_PCT, False)

    def get_cri_dmg(self):
        return self.get_stat(RuneInstance.STAT_CRIT_DMG_PCT, False)

    def get_res(self):
        return self.get_stat(RuneInstance.STAT_RESIST_PCT, False)

    def get_acc(self):
        return self.get_stat(RuneInstance.STAT_ACCURACY_PCT, False)

    def update_fields(self):
        super(RuneInstance, self).update_fields()

        # Check no other runes are in this slot
        if self.assigned_to:
            for rune in RuneInstance.objects.filter(assigned_to=self.assigned_to, slot=self.slot):
                rune.assigned_to = None
                rune.save()

    def clean(self):
        # if self.substat_1 is not None:
        #     if self.substat_1_value is None or self.substat_1_value <= 0:
        #         raise ValidationError({
        #             'substat_1_value': ValidationError(
        #                 'Must be greater than 0.',
        #                 code='invalid_rune_substat_1_value'
        #             )
        #         })
        #     if self.substat_1_craft in RuneCraftInstance.CRAFT_ENCHANT_GEMS:
        #         max_sub_value = RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_1_craft][self.substat_1][
        #             RuneCraftInstance.QUALITY_LEGEND]['max']
        #     else:
        #         max_sub_value = self.SUBSTAT_INCREMENTS[self.substat_1][self.stars] * int(
        #             floor(min(self.level, 12) / 3) + 1)
        #         if self.substat_1_craft in RuneCraftInstance.CRAFT_GRINDSTONES:
        #             max_sub_value += RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_1_craft][self.substat_1][RuneCraftInstance.QUALITY_LEGEND]['max']
        #
        #     # TODO: Remove not ancient check once ancient max substat values are found
        #     if self.substat_1_value > max_sub_value and not self.ancient:
        #         raise ValidationError({
        #             'substat_1_value': ValidationError(
        #                 'Must be less than or equal to ' + str(max_sub_value) + '.',
        #                 code='invalid_rune_substat_1_value'
        #             )
        #         })
        # else:
        #     self.substat_1_value = None
        #     self.substat_1_craft = None
        #
        # if self.substat_2 is not None:
        #     if self.substat_2_value is None or self.substat_2_value <= 0:
        #         raise ValidationError({
        #             'substat_2_value': ValidationError(
        #                 'Must be greater than 0.',
        #                 code='invalid_rune_substat_2_value'
        #             )
        #         })
        #     if self.substat_2_craft in RuneCraftInstance.CRAFT_ENCHANT_GEMS:
        #         max_sub_value = RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_2_craft][self.substat_2][
        #             RuneCraftInstance.QUALITY_LEGEND]['max']
        #     else:
        #         max_sub_value = self.SUBSTAT_INCREMENTS[self.substat_2][self.stars] * int(
        #             floor(min(self.level, 12) / 3) + 1)
        #         if self.substat_2_craft in RuneCraftInstance.CRAFT_GRINDSTONES:
        #             max_sub_value += RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_2_craft][self.substat_2][RuneCraftInstance.QUALITY_LEGEND]['max']
        #
        #     # TODO: Remove not ancient check once ancient max substat values are found
        #     if self.substat_2_value > max_sub_value and not self.ancient:
        #         raise ValidationError({
        #             'substat_2_value': ValidationError(
        #                 'Must be less than or equal to ' + str(max_sub_value) + '.',
        #                 code='invalid_rune_substat_2_value'
        #             )
        #         })
        # else:
        #     self.substat_2_value = None
        #     self.substat_2_craft = None
        #
        # if self.substat_3 is not None:
        #     if self.substat_3_value is None or self.substat_3_value <= 0:
        #         raise ValidationError({
        #             'substat_3_value': ValidationError(
        #                 'Must be greater than 0.',
        #                 code='invalid_rune_substat_3_value'
        #             )
        #         })
        #
        #     if self.substat_3_craft in RuneCraftInstance.CRAFT_ENCHANT_GEMS:
        #         max_sub_value = RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_3_craft][self.substat_3][
        #             RuneCraftInstance.QUALITY_LEGEND]['max']
        #     else:
        #         max_sub_value = self.SUBSTAT_INCREMENTS[self.substat_3][self.stars] * int(
        #             floor(min(self.level, 12) / 3) + 1)
        #         if self.substat_3_craft in RuneCraftInstance.CRAFT_GRINDSTONES:
        #             max_sub_value += RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_3_craft][self.substat_3][RuneCraftInstance.QUALITY_LEGEND]['max']
        #
        #     # TODO: Remove not ancient check once ancient max substat values are found
        #     if self.substat_3_value > max_sub_value and not self.ancient:
        #         raise ValidationError({
        #             'substat_3_value': ValidationError(
        #                 'Must be less than ' + str(max_sub_value) + '.',
        #                 code='invalid_rune_substat_3_value'
        #             )
        #         })
        # else:
        #     self.substat_3_value = None
        #     self.substat_3_craft = None
        #
        # if self.substat_4 is not None:
        #     if self.substat_4_value is None or self.substat_4_value <= 0:
        #         raise ValidationError({
        #             'substat_4_value': ValidationError(
        #                 'Must be greater than 0.',
        #                 code='invalid_rune_substat_4_value'
        #             )
        #         })
        #     if self.substat_4_craft in RuneCraftInstance.CRAFT_ENCHANT_GEMS:
        #         max_sub_value = RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_4_craft][self.substat_4][
        #             RuneCraftInstance.QUALITY_LEGEND]['max']
        #     else:
        #         max_sub_value = self.SUBSTAT_INCREMENTS[self.substat_4][self.stars] * int(
        #             floor(min(self.level, 12) / 3) + 1)
        #         if self.substat_4_craft == RuneCraftInstance.CRAFT_GRINDSTONES:
        #             max_sub_value += RuneCraftInstance.CRAFT_VALUE_RANGES[self.substat_4_craft][self.substat_4][RuneCraftInstance.QUALITY_LEGEND]['max']
        #
        #     # TODO: Remove not ancient check once ancient max substat values are found
        #     if self.substat_4_value > max_sub_value and not self.ancient:
        #         raise ValidationError({
        #             'substat_4_value': ValidationError(
        #                 'Must be less than or equal to ' + str(max_sub_value) + '.',
        #                 code='invalid_rune_substat_4_value'
        #             )
        #         })
        # else:
        #     self.substat_4_value = None
        #     self.substat_4_craft = None

        # Check that monster rune is assigned to does not already have rune in that slot
        if self.assigned_to is not None and (self.assigned_to.runeinstance_set.filter(slot=self.slot).exclude(pk=self.pk).count() > 0):
            raise ValidationError(
                'Monster already has rune in slot %(slot)s. Either pick a different slot or do not assign to the monster yet.',
                params={
                    'slot': self.slot,
                },
                code='slot_occupied'
            )

        # self.update_substat_arrays()
        super(RuneInstance, self).clean()

    def save(self, *args, **kwargs):
        super(RuneInstance, self).save(*args, **kwargs)

        # Trigger stat calc update on the assigned monster
        if self.assigned_to:
            self.assigned_to.save()


class RuneCraftInstance(RuneCraft):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    com2us_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['type', 'rune']


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
