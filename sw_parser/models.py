from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify

from herders.models import Summoner
from bestiary.models import Monster


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


class LogEntry(models.Model):
    # Abstract model with basic fields required for logging anything

    wizard_id = models.BigIntegerField()
    summoner = models.ForeignKey(Summoner, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    server = models.IntegerField(choices=Summoner.SERVER_CHOICES, null=True, blank=True)

    class Meta:
        abstract = True


# Summons
class SummonLog(LogEntry):
    SCROLL_UNKNOWN = 0
    SOCIAL_POINTS = 1
    SCROLL_MYSTICAL = 2
    SUMMON_MYSTICAL = 3
    SCROLL_FIRE = 4
    SCROLL_WATER = 5
    SCROLL_WIND = 6
    SCROLL_LIGHT_AND_DARK = 7
    SCROLL_LEGENDARY = 8
    SUMMON_EXCLUSIVE = 9
    SUMMON_LIGHT_AND_DARK_PIECES = 10
    SUMMON_LEGENDARY_PIECES = 11
    SCROLL_TRANSCENDANCE = 12

    SUMMON_CHOICES = [
        (SCROLL_UNKNOWN, 'Unknown Scroll'),
        (SOCIAL_POINTS, 'Social Summon'),
        (SCROLL_MYSTICAL, 'Mystical Scroll'),
        (SUMMON_MYSTICAL, 'Mystical Summon (Crystals)'),
        (SCROLL_FIRE, 'Fire Scroll'),
        (SCROLL_WATER, 'Water Scroll'),
        (SCROLL_WIND, 'Wind Scroll'),
        (SCROLL_LIGHT_AND_DARK, 'Scroll of Light and Dark'),
        (SCROLL_LEGENDARY, 'Legendary Scroll'),
        (SUMMON_EXCLUSIVE, 'Exclusive Summon (Stones)'),
        (SUMMON_LIGHT_AND_DARK_PIECES, 'Light and Dark Pieces'),
        (SUMMON_LEGENDARY_PIECES, 'Legendary Pieces'),
        (SCROLL_TRANSCENDANCE, 'Transcendance Scroll'),
    ]

    SUMMON_CHOICES_DICT = dict((k, slugify(v)) for k, v in SUMMON_CHOICES)

    monster = models.ForeignKey('MonsterDrop')
    summon_method = models.IntegerField(choices=SUMMON_CHOICES)

    @staticmethod
    def get_summon_method_id(method_slug):
        reverse_dict = dict((v, k) for k, v in SummonLog.SUMMON_CHOICES_DICT.iteritems())
        return reverse_dict.get(method_slug)


# Runs
class RunLog(LogEntry):
    DIFFICULTY_NORMAL = 0
    DIFFICULTY_HARD = 1
    DIFFICULTY_HELL = 2
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_NORMAL, 'Normal'),
        (DIFFICULTY_HARD, 'Hard'),
        (DIFFICULTY_HELL, 'Hell'),
    ]

    FLOOR_CHOICES = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
    ]

    DROP_MONSTER = 100
    DROP_RUNE = 101
    DROP_COSTUME_POINT = 102
    DROP_UPGRADE_STONE = 103
    DROP_SUMMON_PIECES = 104
    DROP_SECRET_DUNGEON = 105
    DROP_ESSENCE_MAGIC_LOW = 110
    DROP_ESSENCE_MAGIC_MID = 111
    DROP_ESSENCE_MAGIC_HIGH = 112
    DROP_ESSENCE_FIRE_LOW = 113
    DROP_ESSENCE_FIRE_MID = 114
    DROP_ESSENCE_FIRE_HIGH = 115
    DROP_ESSENCE_WATER_LOW = 116
    DROP_ESSENCE_WATER_MID = 117
    DROP_ESSENCE_WATER_HIGH = 118
    DROP_ESSENCE_WIND_LOW = 119
    DROP_ESSENCE_WIND_MID = 120
    DROP_ESSENCE_WIND_HIGH = 121
    DROP_ESSENCE_LIGHT_LOW = 122
    DROP_ESSENCE_LIGHT_MID = 123
    DROP_ESSENCE_LIGHT_HIGH = 124
    DROP_ESSENCE_DARK_LOW = 125
    DROP_ESSENCE_DARK_MID = 126
    DROP_ESSENCE_DARK_HIGH = 127
    DROP_CRAFT_WOOD = 128
    DROP_CRAFT_LEATHER = 129
    DROP_CRAFT_ROCK = 130
    DROP_CRAFT_ORE = 131
    DROP_CRAFT_MITHRIL = 132
    DROP_CRAFT_CLOTH = 133
    DROP_CRAFT_RUNE_PIECE = 134
    DROP_CRAFT_POWDER = 135
    DROP_CRAFT_SYMBOL_HARMONY = 136
    DROP_CRAFT_SYMBOL_TRANSCENDANCE = 137
    DROP_CRAFT_SYMBOL_CHAOS = 138
    DROP_CRAFT_CRYSTAL_WATER = 139
    DROP_CRAFT_CRYSTAL_FIRE = 140
    DROP_CRAFT_CRYSTAL_WIND = 141
    DROP_CRAFT_CRYSTAL_LIGHT = 142
    DROP_CRAFT_CRYSTAL_DARK = 143
    DROP_CRAFT_CRYSTAL_MAGIC = 144
    DROP_CRAFT_CRYSTAL_PURE = 145

    DROP_CHOICES = SummonLog.SUMMON_CHOICES + [
        (DROP_MONSTER, 'Monster'),
        (DROP_RUNE, 'Rune'),
        (DROP_COSTUME_POINT, 'Shapeshifting Stone'),
        (DROP_UPGRADE_STONE, 'Power Stone'),
        (DROP_SUMMON_PIECES, 'Summoning Pieces'),
        (DROP_SECRET_DUNGEON, 'Secret Dungeon'),
        (DROP_ESSENCE_MAGIC_LOW, 'Low Magic Essence'),
        (DROP_ESSENCE_MAGIC_MID, 'Mid Magic Essence'),
        (DROP_ESSENCE_MAGIC_HIGH, 'High Magic Essence'),
        (DROP_ESSENCE_FIRE_LOW, 'Low Fire Essence'),
        (DROP_ESSENCE_FIRE_MID, 'Mid Fire Essence'),
        (DROP_ESSENCE_FIRE_HIGH, 'High Fire Essence'),
        (DROP_ESSENCE_WATER_LOW, 'Low Water Essence'),
        (DROP_ESSENCE_WATER_MID, 'Mid Water Essence'),
        (DROP_ESSENCE_WATER_HIGH, 'High Water Essence'),
        (DROP_ESSENCE_WIND_LOW, 'Low Wind Essence'),
        (DROP_ESSENCE_WIND_MID, 'Mid Wind Essence'),
        (DROP_ESSENCE_WIND_HIGH, 'High Wind Essence'),
        (DROP_ESSENCE_LIGHT_LOW, 'Low Light Essence'),
        (DROP_ESSENCE_LIGHT_MID, 'Mid Light Essence'),
        (DROP_ESSENCE_LIGHT_HIGH, 'High Light Essence'),
        (DROP_ESSENCE_DARK_LOW, 'Low Dark Essence'),
        (DROP_ESSENCE_DARK_MID, 'Mid Dark Essence'),
        (DROP_ESSENCE_DARK_HIGH, 'High Dark Essence'),
        (DROP_CRAFT_WOOD, 'Hard Wood',),
        (DROP_CRAFT_LEATHER, 'Tough Leather',),
        (DROP_CRAFT_ROCK, 'Solid Rock',),
        (DROP_CRAFT_ORE, 'Solid Iron Ore',),
        (DROP_CRAFT_MITHRIL, 'Shining Mithril',),
        (DROP_CRAFT_CLOTH, 'Thick Cloth',),
        (DROP_CRAFT_RUNE_PIECE, 'Rune Piece',),
        (DROP_CRAFT_POWDER, 'Magic Dust',),
        (DROP_CRAFT_SYMBOL_HARMONY, 'Symbol of Harmony',),
        (DROP_CRAFT_SYMBOL_TRANSCENDANCE, 'Symbol of Transcendance',),
        (DROP_CRAFT_SYMBOL_CHAOS, 'Symbol of Chaos',),
        (DROP_CRAFT_CRYSTAL_WATER, 'Frozen Water Crystal',),
        (DROP_CRAFT_CRYSTAL_FIRE, 'Flaming Fire Crystal',),
        (DROP_CRAFT_CRYSTAL_WIND, 'Whirling Wind Crystal',),
        (DROP_CRAFT_CRYSTAL_LIGHT, 'Shiny Light Crystal',),
        (DROP_CRAFT_CRYSTAL_DARK, 'Pitch-black Dark Crystal',),
        (DROP_CRAFT_CRYSTAL_MAGIC, 'Condensed Magic Crystal',),
        (DROP_CRAFT_CRYSTAL_PURE, 'Pure Magic Crystal',),
    ]

    DROP_GENERAL_CRAFTS = [
        DROP_CRAFT_WOOD,
        DROP_CRAFT_LEATHER,
        DROP_CRAFT_ROCK,
        DROP_CRAFT_ORE,
        DROP_CRAFT_MITHRIL,
        DROP_CRAFT_CLOTH,
        DROP_CRAFT_POWDER,
    ]

    DROP_RUNE_CRAFTS = [
        DROP_CRAFT_RUNE_PIECE,
        DROP_CRAFT_SYMBOL_HARMONY,
        DROP_CRAFT_SYMBOL_TRANSCENDANCE,
        DROP_CRAFT_SYMBOL_CHAOS,
    ]

    DROP_ESSENCES = [
        DROP_ESSENCE_MAGIC_LOW,
        DROP_ESSENCE_MAGIC_MID,
        DROP_ESSENCE_MAGIC_HIGH,
        DROP_ESSENCE_FIRE_LOW,
        DROP_ESSENCE_FIRE_MID,
        DROP_ESSENCE_FIRE_HIGH,
        DROP_ESSENCE_WATER_LOW,
        DROP_ESSENCE_WATER_MID,
        DROP_ESSENCE_WATER_HIGH,
        DROP_ESSENCE_WIND_LOW,
        DROP_ESSENCE_WIND_MID,
        DROP_ESSENCE_WIND_HIGH,
        DROP_ESSENCE_LIGHT_LOW,
        DROP_ESSENCE_LIGHT_MID,
        DROP_ESSENCE_LIGHT_HIGH,
        DROP_ESSENCE_DARK_LOW,
        DROP_ESSENCE_DARK_MID,
        DROP_ESSENCE_DARK_HIGH,
    ]

    DROP_ITEMS = [
        SummonLog.SCROLL_UNKNOWN,
        SummonLog.SCROLL_MYSTICAL,
        SummonLog.SCROLL_FIRE,
        SummonLog.SCROLL_WATER,
        SummonLog.SCROLL_WIND,
        SummonLog.SCROLL_LEGENDARY,
        SummonLog.SCROLL_LIGHT_AND_DARK,
        SummonLog.SCROLL_TRANSCENDANCE,
        DROP_COSTUME_POINT,
        DROP_UPGRADE_STONE,
        DROP_CRAFT_WOOD,
        DROP_CRAFT_LEATHER,
        DROP_CRAFT_ROCK,
        DROP_CRAFT_ORE,
        DROP_CRAFT_MITHRIL,
        DROP_CRAFT_CLOTH,
        DROP_CRAFT_RUNE_PIECE,
        DROP_CRAFT_POWDER,
        DROP_CRAFT_SYMBOL_HARMONY,
        DROP_CRAFT_SYMBOL_TRANSCENDANCE,
        DROP_CRAFT_SYMBOL_CHAOS,
        DROP_CRAFT_CRYSTAL_WATER,
        DROP_CRAFT_CRYSTAL_FIRE,
        DROP_CRAFT_CRYSTAL_WIND,
        DROP_CRAFT_CRYSTAL_LIGHT,
        DROP_CRAFT_CRYSTAL_DARK,
        DROP_CRAFT_CRYSTAL_MAGIC,
        DROP_CRAFT_CRYSTAL_PURE,
    ]

    DROP_ICONS = {
        SummonLog.SCROLL_UNKNOWN: 'icons/scroll_unknown.png',
        SummonLog.SCROLL_MYSTICAL: 'icons/scroll_mystical.png',
        SummonLog.SCROLL_FIRE: 'icons/scroll_fire.png',
        SummonLog.SCROLL_WATER: 'icons/scroll_water.png',
        SummonLog.SCROLL_WIND: 'icons/scroll_wind.png',
        SummonLog.SCROLL_LEGENDARY: 'icons/scroll_legendary.png',
        SummonLog.SCROLL_LIGHT_AND_DARK: 'icons/scroll_light_and_dark.png',
        SummonLog.SCROLL_TRANSCENDANCE: 'icons/scroll_transcendance.png',
        DROP_COSTUME_POINT: 'icons/costume_stone.png',
        DROP_UPGRADE_STONE: 'icons/power_stone.png',
        DROP_ESSENCE_MAGIC_LOW: 'essences/magic_low.png',
        DROP_ESSENCE_MAGIC_MID: 'essences/magic_mid.png',
        DROP_ESSENCE_MAGIC_HIGH: 'essences/magic_high.png',
        DROP_ESSENCE_FIRE_LOW: 'essences/fire_low.png',
        DROP_ESSENCE_FIRE_MID: 'essences/fire_mid.png',
        DROP_ESSENCE_FIRE_HIGH: 'essences/fire_high.png',
        DROP_ESSENCE_WATER_LOW: 'essences/water_low.png',
        DROP_ESSENCE_WATER_MID: 'essences/water_mid.png',
        DROP_ESSENCE_WATER_HIGH: 'essences/water_high.png',
        DROP_ESSENCE_WIND_LOW: 'essences/wind_low.png',
        DROP_ESSENCE_WIND_MID: 'essences/wind_mid.png',
        DROP_ESSENCE_WIND_HIGH: 'essences/wind_high.png',
        DROP_ESSENCE_LIGHT_LOW: 'essences/light_low.png',
        DROP_ESSENCE_LIGHT_MID: 'essences/light_mid.png',
        DROP_ESSENCE_LIGHT_HIGH: 'essences/light_high.png',
        DROP_ESSENCE_DARK_LOW: 'essences/dark_low.png',
        DROP_ESSENCE_DARK_MID: 'essences/dark_mid.png',
        DROP_ESSENCE_DARK_HIGH: 'essences/dark_high.png',
        DROP_CRAFT_WOOD: 'crafts/wood.png',
        DROP_CRAFT_LEATHER: 'crafts/leather.png',
        DROP_CRAFT_ROCK: 'crafts/rock.png',
        DROP_CRAFT_ORE: 'crafts/ore.png',
        DROP_CRAFT_MITHRIL: 'crafts/mithril.png',
        DROP_CRAFT_CLOTH: 'crafts/cloth.png',
        DROP_CRAFT_RUNE_PIECE: 'crafts/rune_piece.png',
        DROP_CRAFT_POWDER: 'crafts/dust.png',
        DROP_CRAFT_SYMBOL_HARMONY: 'crafts/symbol_harmony.png',
        DROP_CRAFT_SYMBOL_TRANSCENDANCE: 'crafts/symbol_transcendance.png',
        DROP_CRAFT_SYMBOL_CHAOS: 'crafts/symbol_chaos.png',
        DROP_CRAFT_CRYSTAL_WATER: 'crafts/water_crystal.png',
        DROP_CRAFT_CRYSTAL_FIRE: 'crafts/fire_crystal.png',
        DROP_CRAFT_CRYSTAL_WIND: 'crafts/wind_crystal.png',
        DROP_CRAFT_CRYSTAL_LIGHT: 'crafts/light_crystal.png',
        DROP_CRAFT_CRYSTAL_DARK: 'crafts/dark_crystal.png',
        DROP_CRAFT_CRYSTAL_MAGIC: 'crafts/magic_crystal.png',
        DROP_CRAFT_CRYSTAL_PURE: 'crafts/pure_crystal.png',
    }

    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    dungeon = models.ForeignKey(Dungeon)
    stage = models.IntegerField(help_text='Floor for Caiross or stage for scenarios', choices=FLOOR_CHOICES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, help_text='For scenarios only', blank=True, null=True)
    success = models.NullBooleanField()  # Null value here is an incomplete record from a log that needs the start and result commands to fill in completely
    clear_time = models.DurationField(blank=True, null=True)
    energy = models.IntegerField(blank=True, null=True)
    mana = models.IntegerField(blank=True, null=True)
    crystal = models.IntegerField(blank=True, null=True)
    drop_type = models.IntegerField(choices=DROP_CHOICES, blank=True, null=True)
    drop_quantity = models.IntegerField(blank=True, null=True)
    drop_monster = models.ForeignKey('MonsterDrop', blank=True, null=True)
    drop_rune = models.ForeignKey('RuneDrop', blank=True, null=True)

    @staticmethod
    def get_drop_type_string(drop):
        for choice in RunLog.DROP_CHOICES:
            if choice[0] == drop:
                return choice[1]

        return None


class RuneDrop(models.Model):
    TYPE_ENERGY = 1
    TYPE_FATAL = 2
    TYPE_BLADE = 3
    TYPE_RAGE = 4
    TYPE_SWIFT = 5
    TYPE_FOCUS = 6
    TYPE_GUARD = 7
    TYPE_ENDURE = 8
    TYPE_VIOLENT = 9
    TYPE_WILL = 10
    TYPE_NEMESIS = 11
    TYPE_SHIELD = 12
    TYPE_REVENGE = 13
    TYPE_DESPAIR = 14
    TYPE_VAMPIRE = 15
    TYPE_DESTROY = 16
    TYPE_FIGHT = 17
    TYPE_DETERMINATION = 18
    TYPE_ENHANCE = 19
    TYPE_ACCURACY = 20
    TYPE_TOLERANCE = 21

    TYPE_CHOICES = [
        (TYPE_ENERGY, 'Energy'),
        (TYPE_FATAL, 'Fatal'),
        (TYPE_BLADE, 'Blade'),
        (TYPE_RAGE, 'Rage'),
        (TYPE_SWIFT, 'Swift'),
        (TYPE_FOCUS, 'Focus'),
        (TYPE_GUARD, 'Guard'),
        (TYPE_ENDURE, 'Endure'),
        (TYPE_VIOLENT, 'Violent'),
        (TYPE_WILL, 'Will'),
        (TYPE_NEMESIS, 'Nemesis'),
        (TYPE_SHIELD, 'Shield'),
        (TYPE_REVENGE, 'Revenge'),
        (TYPE_DESPAIR, 'Despair'),
        (TYPE_VAMPIRE, 'Vampire'),
        (TYPE_DESTROY, 'Destroy'),
        (TYPE_FIGHT, 'Fight'),
        (TYPE_DETERMINATION, 'Determination'),
        (TYPE_ENHANCE, 'Enhance'),
        (TYPE_ACCURACY, 'Accuracy'),
        (TYPE_TOLERANCE, 'Tolerance'),
    ]

    STAR_CHOICES = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    ]

    STAT_HP = 1
    STAT_HP_PCT = 2
    STAT_ATK = 3
    STAT_ATK_PCT = 4
    STAT_DEF = 5
    STAT_DEF_PCT = 6
    STAT_SPD = 7
    STAT_CRIT_RATE_PCT = 8
    STAT_CRIT_DMG_PCT = 9
    STAT_RESIST_PCT = 10
    STAT_ACCURACY_PCT = 11

    # Used for selecting type of stat in form
    STAT_CHOICES = [
        (STAT_HP, 'HP'),
        (STAT_HP_PCT, 'HP %'),
        (STAT_ATK, 'ATK'),
        (STAT_ATK_PCT, 'ATK %'),
        (STAT_DEF, 'DEF'),
        (STAT_DEF_PCT, 'DEF %'),
        (STAT_SPD, 'SPD'),
        (STAT_CRIT_RATE_PCT, 'CRI Rate %'),
        (STAT_CRIT_DMG_PCT, 'CRI Dmg %'),
        (STAT_RESIST_PCT, 'Resistance %'),
        (STAT_ACCURACY_PCT, 'Accuracy %'),
    ]

    RUNE_STAT_DISPLAY = {
        STAT_HP: 'HP',
        STAT_HP_PCT: 'HP',
        STAT_ATK: 'ATK',
        STAT_ATK_PCT: 'ATK',
        STAT_DEF: 'DEF',
        STAT_DEF_PCT: 'DEF',
        STAT_SPD: 'SPD',
        STAT_CRIT_RATE_PCT: 'CRI Rate',
        STAT_CRIT_DMG_PCT: 'CRI Dmg',
        STAT_RESIST_PCT: 'Resistance',
        STAT_ACCURACY_PCT: 'Accuracy',
    }

    PERCENT_STATS = [
        STAT_HP_PCT,
        STAT_ATK_PCT,
        STAT_DEF_PCT,
        STAT_CRIT_RATE_PCT,
        STAT_CRIT_DMG_PCT,
        STAT_RESIST_PCT,
        STAT_ACCURACY_PCT,
    ]

    FLAT_STATS = [
        STAT_HP,
        STAT_ATK,
        STAT_DEF,
        STAT_SPD,
    ]

    MAIN_STAT_VALUES = {
        # [stat][stars][level]: value
        STAT_HP: {
            1: [40, 85, 130, 175, 220, 265, 310, 355, 400, 445, 490, 535, 580, 625, 670, 804],
            2: [70, 130, 190, 250, 310, 370, 430, 490, 550, 610, 670, 730, 790, 850, 910, 1092],
            3: [100, 175, 250, 325, 400, 475, 550, 625, 700, 775, 850, 925, 1000, 1075, 1150, 1380],
            4: [160, 250, 340, 430, 520, 610, 700, 790, 880, 970, 1060, 1150, 1240, 1330, 1420, 1704],
            5: [270, 375, 480, 585, 690, 795, 900, 1005, 1110, 1215, 1320, 1425, 1530, 1635, 1740, 2088],
            6: [360, 480, 600, 720, 840, 960, 1080, 1200, 1320, 1440, 1560, 1680, 1800, 1920, 2040, 2448],
        },
        STAT_HP_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        STAT_ATK: {
            1: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
            2: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
            3: [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
            4: [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
            5: [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
            6: [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160],
        },
        STAT_ATK_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        STAT_DEF: {
            1: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
            2: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
            3: [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
            4: [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
            5: [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
            6: [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160],
        },
        STAT_DEF_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        STAT_SPD: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 25],
            4: [4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 30],
            5: [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 39],
            6: [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 42],
        },
        STAT_CRIT_RATE_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
            4: [4, 6, 8, 11, 13, 15, 17, 19, 22, 24, 26, 28, 30, 33, 35, 41],
            5: [5, 7, 10, 12, 15, 17, 19, 22, 24, 27, 29, 31, 34, 36, 39, 47],
            6: [7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 58],
        },
        STAT_CRIT_DMG_PCT: {
            1: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            2: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
            3: [4, 6, 9, 11, 13, 16, 18, 20, 22, 25, 27, 29, 32, 34, 36, 43],
            4: [6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 57],
            5: [8, 11, 15, 18, 21, 25, 28, 31, 34, 38, 41, 44, 48, 51, 54, 65],
            6: [11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67, 80],
        },
        STAT_RESIST_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
            5: [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
            6: [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64],
        },
        STAT_ACCURACY_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
            5: [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
            6: [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64],
        },
    }

    SUBSTAT_INCREMENTS = {
        # [stat][stars]: value
        # Max possible substat value can be found by multiplying by 5
        STAT_HP: {
            1: 60,
            2: 105,
            3: 165,
            4: 225,
            5: 300,
            6: 375,
        },
        STAT_HP_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        STAT_ATK: {
            1: 4,
            2: 5,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
        },
        STAT_ATK_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        STAT_DEF: {
            1: 4,
            2: 5,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
        },
        STAT_DEF_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        STAT_SPD: {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
        },
        STAT_CRIT_RATE_PCT: {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
        },
        STAT_CRIT_DMG_PCT: {
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
        },
        STAT_RESIST_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        STAT_ACCURACY_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
    }

    QUALITY_NORMAL = 0
    QUALITY_MAGIC = 1
    QUALITY_RARE = 2
    QUALITY_HERO = 3
    QUALITY_LEGEND = 4

    QUALITY_CHOICES = (
        (QUALITY_NORMAL, 'Normal'),
        (QUALITY_MAGIC, 'Magic'),
        (QUALITY_RARE, 'Rare'),
        (QUALITY_HERO, 'Hero'),
        (QUALITY_LEGEND, 'Legend'),
    )

    QUALITY_COLORS = {
        QUALITY_NORMAL: '#eeeeee',
        QUALITY_MAGIC: '#04d25e',
        QUALITY_RARE: '#3bc9fe',
        QUALITY_HERO: '#d66ef6',
        QUALITY_LEGEND: '#ef9f24',
    }

    type = models.IntegerField(choices=TYPE_CHOICES)
    stars = models.IntegerField()
    slot = models.IntegerField()
    value = models.IntegerField()
    quality = models.IntegerField(default=0, choices=QUALITY_CHOICES)
    max_efficiency = models.FloatField()
    main_stat = models.IntegerField(choices=STAT_CHOICES)
    main_stat_value = models.IntegerField()
    innate_stat = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    innate_stat_value = models.IntegerField(null=True, blank=True)
    substat_1 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_1_value = models.IntegerField(null=True, blank=True)
    substat_2 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_2_value = models.IntegerField(null=True, blank=True)
    substat_3 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_3_value = models.IntegerField(null=True, blank=True)
    substat_4 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_4_value = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.get_type_display() + ' ' + str(self.stars) + '* - Slot ' + str(self.slot) + ' - ' + self.get_main_stat_display()

    def get_max_efficiency(self):
        running_sum = 0.8  # 0.8 accounts for assumed perfect upgrades on the remaining 4 substat upgrades.

        # Main stat efficiency
        running_sum += float(self.MAIN_STAT_VALUES[self.main_stat][self.stars][15]) / float(self.MAIN_STAT_VALUES[self.main_stat][6][15])

        # Substat efficiencies
        if self.innate_stat is not None:
            running_sum += self.innate_stat_value / float(self.SUBSTAT_INCREMENTS[self.innate_stat][6] * 5)

        if self.substat_1 is not None:
            running_sum += self.substat_1_value / float(self.SUBSTAT_INCREMENTS[self.substat_1][6] * 5)

        if self.substat_2 is not None:
            running_sum += self.substat_2_value / float(self.SUBSTAT_INCREMENTS[self.substat_2][6] * 5)

        if self.substat_3 is not None:
            running_sum += self.substat_3_value / float(self.SUBSTAT_INCREMENTS[self.substat_3][6] * 5)

        if self.substat_4 is not None:
            running_sum += self.substat_4_value / float(self.SUBSTAT_INCREMENTS[self.substat_4][6] * 5)

        return running_sum / 2.8 * 100

    def save(self, *args, **kwargs):
        self.quality = len(filter(None, [self.substat_1, self.substat_2, self.substat_3, self.substat_4]))
        self.max_efficiency = self.get_max_efficiency()
        super(RuneDrop, self).save(*args, **kwargs)


class RuneCraftDrop(models.Model):
    CRAFT_GRINDSTONE = 0
    CRAFT_ENCHANT_GEM = 1

    CRAFT_CHOICES = (
        (CRAFT_GRINDSTONE, 'Grindstone'),
        (CRAFT_ENCHANT_GEM, 'Enchant Gem'),
    )

    QUALITY_NORMAL = 0
    QUALITY_MAGIC = 1
    QUALITY_RARE = 2
    QUALITY_HERO = 3
    QUALITY_LEGEND = 4

    QUALITY_CHOICES = (
        (QUALITY_NORMAL, 'Normal'),
        (QUALITY_MAGIC, 'Magic'),
        (QUALITY_RARE, 'Rare'),
        (QUALITY_HERO, 'Hero'),
        (QUALITY_LEGEND, 'Legend'),
    )

    # Valid value ranges
    # Type > Stat > Quality > Min/Max
    CRAFT_VALUE_RANGES = {
        CRAFT_GRINDSTONE: {
            RuneDrop.STAT_HP: {
                RuneDrop.QUALITY_NORMAL: {'min': 80, 'max': 120},
                RuneDrop.QUALITY_MAGIC: {'min': 100, 'max': 200},
                RuneDrop.QUALITY_RARE: {'min': 180, 'max': 250},
                RuneDrop.QUALITY_HERO: {'min': 230, 'max': 450},
                RuneDrop.QUALITY_LEGEND: {'min': 430, 'max': 550},
            },
            RuneDrop.STAT_HP_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneDrop.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneDrop.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneDrop.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneDrop.STAT_ATK: {
                RuneDrop.QUALITY_NORMAL: {'min': 4, 'max': 8},
                RuneDrop.QUALITY_MAGIC: {'min': 6, 'max': 12},
                RuneDrop.QUALITY_RARE: {'min': 10, 'max': 18},
                RuneDrop.QUALITY_HERO: {'min': 12, 'max': 22},
                RuneDrop.QUALITY_LEGEND: {'min': 18, 'max': 30},
            },
            RuneDrop.STAT_ATK_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneDrop.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneDrop.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneDrop.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneDrop.STAT_DEF: {
                RuneDrop.QUALITY_NORMAL: {'min': 4, 'max': 8},
                RuneDrop.QUALITY_MAGIC: {'min': 6, 'max': 12},
                RuneDrop.QUALITY_RARE: {'min': 10, 'max': 18},
                RuneDrop.QUALITY_HERO: {'min': 12, 'max': 22},
                RuneDrop.QUALITY_LEGEND: {'min': 18, 'max': 30},
            },
            RuneDrop.STAT_DEF_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneDrop.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneDrop.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneDrop.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneDrop.STAT_SPD: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneDrop.QUALITY_MAGIC: {'min': 1, 'max': 2},
                RuneDrop.QUALITY_RARE: {'min': 2, 'max': 3},
                RuneDrop.QUALITY_HERO: {'min': 3, 'max': 4},
                RuneDrop.QUALITY_LEGEND: {'min': 4, 'max': 5},
            },
            RuneDrop.STAT_CRIT_RATE_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneDrop.QUALITY_MAGIC: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_RARE: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneDrop.QUALITY_LEGEND: {'min': 4, 'max': 6},
            },
            RuneDrop.STAT_CRIT_DMG_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneDrop.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneDrop.QUALITY_LEGEND: {'min': 4, 'max': 7},
            },
            RuneDrop.STAT_RESIST_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneDrop.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneDrop.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
            RuneDrop.STAT_ACCURACY_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneDrop.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneDrop.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
        },
        CRAFT_ENCHANT_GEM: {
            RuneDrop.STAT_HP: {
                RuneDrop.QUALITY_NORMAL: {'min': 100, 'max': 150},
                RuneDrop.QUALITY_MAGIC: {'min': 130, 'max': 220},
                RuneDrop.QUALITY_RARE: {'min': 200, 'max': 310},
                RuneDrop.QUALITY_HERO: {'min': 290, 'max': 420},
                RuneDrop.QUALITY_LEGEND: {'min': 400, 'max': 580},
            },
            RuneDrop.STAT_HP_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneDrop.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneDrop.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneDrop.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneDrop.STAT_ATK: {
                RuneDrop.QUALITY_NORMAL: {'min': 8, 'max': 12},
                RuneDrop.QUALITY_MAGIC: {'min': 10, 'max': 16},
                RuneDrop.QUALITY_RARE: {'min': 15, 'max': 23},
                RuneDrop.QUALITY_HERO: {'min': 20, 'max': 30},
                RuneDrop.QUALITY_LEGEND: {'min': 28, 'max': 40},
            },
            RuneDrop.STAT_ATK_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneDrop.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneDrop.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneDrop.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneDrop.STAT_DEF: {
                RuneDrop.QUALITY_NORMAL: {'min': 8, 'max': 12},
                RuneDrop.QUALITY_MAGIC: {'min': 10, 'max': 16},
                RuneDrop.QUALITY_RARE: {'min': 15, 'max': 23},
                RuneDrop.QUALITY_HERO: {'min': 20, 'max': 30},
                RuneDrop.QUALITY_LEGEND: {'min': 28, 'max': 40},
            },
            RuneDrop.STAT_DEF_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneDrop.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneDrop.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneDrop.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneDrop.STAT_SPD: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneDrop.QUALITY_HERO: {'min': 5, 'max': 8},
                RuneDrop.QUALITY_LEGEND: {'min': 7, 'max': 10},
            },
            RuneDrop.STAT_CRIT_RATE_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneDrop.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_RARE: {'min': 3, 'max': 5},
                RuneDrop.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneDrop.QUALITY_LEGEND: {'min': 6, 'max': 9},
            },
            RuneDrop.STAT_CRIT_DMG_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_MAGIC: {'min': 3, 'max': 5},
                RuneDrop.QUALITY_RARE: {'min': 4, 'max': 6},
                RuneDrop.QUALITY_HERO: {'min': 5, 'max': 8},
                RuneDrop.QUALITY_LEGEND: {'min': 7, 'max': 10},
            },
            RuneDrop.STAT_RESIST_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_MAGIC: {'min': 3, 'max': 6},
                RuneDrop.QUALITY_RARE: {'min': 5, 'max': 8},
                RuneDrop.QUALITY_HERO: {'min': 6, 'max': 9},
                RuneDrop.QUALITY_LEGEND: {'min': 8, 'max': 11},
            },
            RuneDrop.STAT_ACCURACY_PCT: {
                RuneDrop.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneDrop.QUALITY_MAGIC: {'min': 3, 'max': 6},
                RuneDrop.QUALITY_RARE: {'min': 5, 'max': 8},
                RuneDrop.QUALITY_HERO: {'min': 6, 'max': 9},
                RuneDrop.QUALITY_LEGEND: {'min': 8, 'max': 11},
            },
        }
    }

    type = models.IntegerField(choices=CRAFT_CHOICES)
    rune = models.IntegerField(choices=RuneDrop.TYPE_CHOICES)
    stat = models.IntegerField(choices=RuneDrop.STAT_CHOICES)
    quality = models.IntegerField(choices=QUALITY_CHOICES)
    value = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.stat in RuneDrop.PERCENT_STATS:
            percent = '%'
        else:
            percent = ''

        return RuneDrop.RUNE_STAT_DISPLAY.get(self.stat) + ' +' + str(self.get_min_value()) + percent + ' - ' + str(self.get_max_value()) + percent

    def get_min_value(self):
        try:
            return self.CRAFT_VALUE_RANGES[self.type][self.stat][self.quality]['min']
        except KeyError:
            return None

    def get_max_value(self):
        try:
            return self.CRAFT_VALUE_RANGES[self.type][self.stat][self.quality]['max']
        except KeyError:
            return None


class MonsterDrop(models.Model):
    monster = models.ForeignKey(Monster)
    grade = models.IntegerField()
    level = models.IntegerField()

    def __str__(self):
        return str(self.monster) + ' ' + str(self.grade) + '*'


class ItemDrop(models.Model):
    DROP_COSTUME_POINT = 102
    DROP_UPGRADE_STONE = 103
    DROP_SUMMON_PIECES = 104
    DROP_SECRET_DUNGEON = 105
    DROP_ESSENCE_MAGIC_LOW = 110
    DROP_ESSENCE_MAGIC_MID = 111
    DROP_ESSENCE_MAGIC_HIGH = 112
    DROP_ESSENCE_FIRE_LOW = 113
    DROP_ESSENCE_FIRE_MID = 114
    DROP_ESSENCE_FIRE_HIGH = 115
    DROP_ESSENCE_WATER_LOW = 116
    DROP_ESSENCE_WATER_MID = 117
    DROP_ESSENCE_WATER_HIGH = 118
    DROP_ESSENCE_WIND_LOW = 119
    DROP_ESSENCE_WIND_MID = 120
    DROP_ESSENCE_WIND_HIGH = 121
    DROP_ESSENCE_LIGHT_LOW = 122
    DROP_ESSENCE_LIGHT_MID = 123
    DROP_ESSENCE_LIGHT_HIGH = 124
    DROP_ESSENCE_DARK_LOW = 125
    DROP_ESSENCE_DARK_MID = 126
    DROP_ESSENCE_DARK_HIGH = 127
    DROP_CRAFT_WOOD = 128
    DROP_CRAFT_LEATHER = 129
    DROP_CRAFT_ROCK = 130
    DROP_CRAFT_ORE = 131
    DROP_CRAFT_MITHRIL = 132
    DROP_CRAFT_CLOTH = 133
    DROP_CRAFT_RUNE_PIECE = 134
    DROP_CRAFT_POWDER = 135
    DROP_CRAFT_SYMBOL_HARMONY = 136
    DROP_CRAFT_SYMBOL_TRANSCENDANCE = 137
    DROP_CRAFT_SYMBOL_CHAOS = 138
    DROP_CRAFT_CRYSTAL_WATER = 139
    DROP_CRAFT_CRYSTAL_FIRE = 140
    DROP_CRAFT_CRYSTAL_WIND = 141
    DROP_CRAFT_CRYSTAL_LIGHT = 142
    DROP_CRAFT_CRYSTAL_DARK = 143
    DROP_CRAFT_CRYSTAL_MAGIC = 144
    DROP_CRAFT_CRYSTAL_PURE = 145
    DROP_CURRENCY_MANA = 146
    DROP_CURRENCY_CRYSTALS = 147
    DROP_CURRENCY_GLORY_POINT = 148
    DROP_CURRENCY_GUILD_POINT = 149
    DROP_CURRENCY_REAL_MONEY = 150

    DROP_CHOICES = SummonLog.SUMMON_CHOICES + [
        (DROP_COSTUME_POINT, 'Shapeshifting Stone'),
        (DROP_UPGRADE_STONE, 'Power Stone'),
        (DROP_SUMMON_PIECES, 'Summoning Pieces'),
        (DROP_SECRET_DUNGEON, 'Secret Dungeon'),
        (DROP_ESSENCE_MAGIC_LOW, 'Low Magic Essence'),
        (DROP_ESSENCE_MAGIC_MID, 'Mid Magic Essence'),
        (DROP_ESSENCE_MAGIC_HIGH, 'High Magic Essence'),
        (DROP_ESSENCE_FIRE_LOW, 'Low Fire Essence'),
        (DROP_ESSENCE_FIRE_MID, 'Mid Fire Essence'),
        (DROP_ESSENCE_FIRE_HIGH, 'High Fire Essence'),
        (DROP_ESSENCE_WATER_LOW, 'Low Water Essence'),
        (DROP_ESSENCE_WATER_MID, 'Mid Water Essence'),
        (DROP_ESSENCE_WATER_HIGH, 'High Water Essence'),
        (DROP_ESSENCE_WIND_LOW, 'Low Wind Essence'),
        (DROP_ESSENCE_WIND_MID, 'Mid Wind Essence'),
        (DROP_ESSENCE_WIND_HIGH, 'High Wind Essence'),
        (DROP_ESSENCE_LIGHT_LOW, 'Low Light Essence'),
        (DROP_ESSENCE_LIGHT_MID, 'Mid Light Essence'),
        (DROP_ESSENCE_LIGHT_HIGH, 'High Light Essence'),
        (DROP_ESSENCE_DARK_LOW, 'Low Dark Essence'),
        (DROP_ESSENCE_DARK_MID, 'Mid Dark Essence'),
        (DROP_ESSENCE_DARK_HIGH, 'High Dark Essence'),
        (DROP_CRAFT_WOOD, 'Hard Wood',),
        (DROP_CRAFT_LEATHER, 'Tough Leather',),
        (DROP_CRAFT_ROCK, 'Solid Rock',),
        (DROP_CRAFT_ORE, 'Solid Iron Ore',),
        (DROP_CRAFT_MITHRIL, 'Shining Mithril',),
        (DROP_CRAFT_CLOTH, 'Thick Cloth',),
        (DROP_CRAFT_RUNE_PIECE, 'Rune Piece',),
        (DROP_CRAFT_POWDER, 'Magic Dust',),
        (DROP_CRAFT_SYMBOL_HARMONY, 'Symbol of Harmony',),
        (DROP_CRAFT_SYMBOL_TRANSCENDANCE, 'Symbol of Transcendance',),
        (DROP_CRAFT_SYMBOL_CHAOS, 'Symbol of Chaos',),
        (DROP_CRAFT_CRYSTAL_WATER, 'Frozen Water Crystal',),
        (DROP_CRAFT_CRYSTAL_FIRE, 'Flaming Fire Crystal',),
        (DROP_CRAFT_CRYSTAL_WIND, 'Whirling Wind Crystal',),
        (DROP_CRAFT_CRYSTAL_LIGHT, 'Shiny Light Crystal',),
        (DROP_CRAFT_CRYSTAL_DARK, 'Pitch-black Dark Crystal',),
        (DROP_CRAFT_CRYSTAL_MAGIC, 'Condensed Magic Crystal',),
        (DROP_CRAFT_CRYSTAL_PURE, 'Pure Magic Crystal',),
        (DROP_CURRENCY_MANA, 'Mana'),
        (DROP_CURRENCY_CRYSTALS, 'Crystals'),
        (DROP_CURRENCY_GLORY_POINT, 'Glory Points'),
        (DROP_CURRENCY_GUILD_POINT, 'Guild Points'),
        (DROP_CURRENCY_REAL_MONEY, 'Real Money'),
    ]

    DROP_CHOICES_DICT = dict(DROP_CHOICES)

    DROP_SUMMONING = [x[0] for x in SummonLog.SUMMON_CHOICES]

    DROP_ESSENCES = [
        DROP_ESSENCE_MAGIC_LOW,
        DROP_ESSENCE_MAGIC_MID,
        DROP_ESSENCE_MAGIC_HIGH,
        DROP_ESSENCE_FIRE_LOW,
        DROP_ESSENCE_FIRE_MID,
        DROP_ESSENCE_FIRE_HIGH,
        DROP_ESSENCE_WATER_LOW,
        DROP_ESSENCE_WATER_MID,
        DROP_ESSENCE_WATER_HIGH,
        DROP_ESSENCE_WIND_LOW,
        DROP_ESSENCE_WIND_MID,
        DROP_ESSENCE_WIND_HIGH,
        DROP_ESSENCE_LIGHT_LOW,
        DROP_ESSENCE_LIGHT_MID,
        DROP_ESSENCE_LIGHT_HIGH,
        DROP_ESSENCE_DARK_LOW,
        DROP_ESSENCE_DARK_MID,
        DROP_ESSENCE_DARK_HIGH,
    ]

    DROP_ITEMS = [
        SummonLog.SCROLL_UNKNOWN,
        SummonLog.SCROLL_MYSTICAL,
        SummonLog.SCROLL_FIRE,
        SummonLog.SCROLL_WATER,
        SummonLog.SCROLL_WIND,
        SummonLog.SCROLL_LEGENDARY,
        SummonLog.SCROLL_LIGHT_AND_DARK,
        SummonLog.SUMMON_LEGENDARY_PIECES,
        SummonLog.SUMMON_LIGHT_AND_DARK_PIECES,
        SummonLog.SCROLL_TRANSCENDANCE,
        DROP_COSTUME_POINT,
        DROP_UPGRADE_STONE,
        DROP_CRAFT_WOOD,
        DROP_CRAFT_LEATHER,
        DROP_CRAFT_ROCK,
        DROP_CRAFT_ORE,
        DROP_CRAFT_MITHRIL,
        DROP_CRAFT_CLOTH,
        DROP_CRAFT_RUNE_PIECE,
        DROP_CRAFT_POWDER,
        DROP_CRAFT_SYMBOL_HARMONY,
        DROP_CRAFT_SYMBOL_TRANSCENDANCE,
        DROP_CRAFT_SYMBOL_CHAOS,
        DROP_CRAFT_CRYSTAL_WATER,
        DROP_CRAFT_CRYSTAL_FIRE,
        DROP_CRAFT_CRYSTAL_WIND,
        DROP_CRAFT_CRYSTAL_LIGHT,
        DROP_CRAFT_CRYSTAL_DARK,
        DROP_CRAFT_CRYSTAL_MAGIC,
        DROP_CRAFT_CRYSTAL_PURE,
    ]

    DROP_GENERAL_CRAFTS = [
        DROP_CRAFT_WOOD,
        DROP_CRAFT_LEATHER,
        DROP_CRAFT_ROCK,
        DROP_CRAFT_ORE,
        DROP_CRAFT_MITHRIL,
        DROP_CRAFT_CLOTH,
        DROP_CRAFT_POWDER,
    ]

    DROP_RUNE_CRAFTS = [
        DROP_CRAFT_RUNE_PIECE,
        DROP_CRAFT_SYMBOL_HARMONY,
        DROP_CRAFT_SYMBOL_TRANSCENDANCE,
        DROP_CRAFT_SYMBOL_CHAOS,
    ]

    DROP_CURRENCY = [
        DROP_CURRENCY_MANA,
        DROP_CURRENCY_CRYSTALS,
        DROP_CURRENCY_GLORY_POINT,
        DROP_CURRENCY_GUILD_POINT,
        DROP_CURRENCY_REAL_MONEY,
    ]

    DROP_ICONS = {
        SummonLog.SCROLL_UNKNOWN: 'icons/scroll_unknown.png',
        SummonLog.SCROLL_MYSTICAL: 'icons/scroll_mystical.png',
        SummonLog.SCROLL_FIRE: 'icons/scroll_fire.png',
        SummonLog.SCROLL_WATER: 'icons/scroll_water.png',
        SummonLog.SCROLL_WIND: 'icons/scroll_wind.png',
        SummonLog.SCROLL_LEGENDARY: 'icons/scroll_legendary.png',
        SummonLog.SCROLL_LIGHT_AND_DARK: 'icons/scroll_light_and_dark.png',
        SummonLog.SUMMON_EXCLUSIVE: 'icons/summon_exclusive.png',
        SummonLog.SUMMON_LEGENDARY_PIECES: 'icons/pieces_legendary.png',
        SummonLog.SUMMON_LIGHT_AND_DARK_PIECES: 'icons/pieces_light_and_dark.png',
        SummonLog.SCROLL_TRANSCENDANCE: 'icons/scroll_transcendance.png',
        DROP_COSTUME_POINT: 'icons/costume_stone.png',
        DROP_UPGRADE_STONE: 'icons/power_stone.png',
        DROP_ESSENCE_MAGIC_LOW: 'essences/magic_low.png',
        DROP_ESSENCE_MAGIC_MID: 'essences/magic_mid.png',
        DROP_ESSENCE_MAGIC_HIGH: 'essences/magic_high.png',
        DROP_ESSENCE_FIRE_LOW: 'essences/fire_low.png',
        DROP_ESSENCE_FIRE_MID: 'essences/fire_mid.png',
        DROP_ESSENCE_FIRE_HIGH: 'essences/fire_high.png',
        DROP_ESSENCE_WATER_LOW: 'essences/water_low.png',
        DROP_ESSENCE_WATER_MID: 'essences/water_mid.png',
        DROP_ESSENCE_WATER_HIGH: 'essences/water_high.png',
        DROP_ESSENCE_WIND_LOW: 'essences/wind_low.png',
        DROP_ESSENCE_WIND_MID: 'essences/wind_mid.png',
        DROP_ESSENCE_WIND_HIGH: 'essences/wind_high.png',
        DROP_ESSENCE_LIGHT_LOW: 'essences/light_low.png',
        DROP_ESSENCE_LIGHT_MID: 'essences/light_mid.png',
        DROP_ESSENCE_LIGHT_HIGH: 'essences/light_high.png',
        DROP_ESSENCE_DARK_LOW: 'essences/dark_low.png',
        DROP_ESSENCE_DARK_MID: 'essences/dark_mid.png',
        DROP_ESSENCE_DARK_HIGH: 'essences/dark_high.png',
        DROP_CRAFT_WOOD: 'crafts/wood.png',
        DROP_CRAFT_LEATHER: 'crafts/leather.png',
        DROP_CRAFT_ROCK: 'crafts/rock.png',
        DROP_CRAFT_ORE: 'crafts/ore.png',
        DROP_CRAFT_MITHRIL: 'crafts/mithril.png',
        DROP_CRAFT_CLOTH: 'crafts/cloth.png',
        DROP_CRAFT_RUNE_PIECE: 'crafts/rune_piece.png',
        DROP_CRAFT_POWDER: 'crafts/dust.png',
        DROP_CRAFT_SYMBOL_HARMONY: 'crafts/symbol_harmony.png',
        DROP_CRAFT_SYMBOL_TRANSCENDANCE: 'crafts/symbol_transcendance.png',
        DROP_CRAFT_SYMBOL_CHAOS: 'crafts/symbol_chaos.png',
        DROP_CRAFT_CRYSTAL_WATER: 'crafts/crystal_water.png',
        DROP_CRAFT_CRYSTAL_FIRE: 'crafts/crystal_fire.png',
        DROP_CRAFT_CRYSTAL_WIND: 'crafts/crystal_wind.png',
        DROP_CRAFT_CRYSTAL_LIGHT: 'crafts/crystal_light.png',
        DROP_CRAFT_CRYSTAL_DARK: 'crafts/crystal_dark.png',
        DROP_CRAFT_CRYSTAL_MAGIC: 'crafts/crystal_magic.png',
        DROP_CRAFT_CRYSTAL_PURE: 'crafts/crystal_pure.png',
        DROP_CURRENCY_MANA: 'icons/mana.png',
        DROP_CURRENCY_CRYSTALS: 'icons/crystal.png',
        DROP_CURRENCY_GUILD_POINT: 'icons/guild_points.png',
        DROP_CURRENCY_GLORY_POINT: 'icons/glory_points.png',
    }

    item = models.IntegerField(choices=DROP_CHOICES)
    quantity = models.IntegerField()

    class Meta:
        abstract = True


# Rift dungeons
class RiftDungeonItemDrop(ItemDrop):
    log = models.ForeignKey('RiftDungeonLog', related_name='item_drops')


class RiftDungeonMonsterDrop(MonsterDrop):
    log = models.ForeignKey('RiftDungeonLog', related_name='monster_drops')


class RiftDungeonLog(LogEntry):
    GRADE_F = 1
    GRADE_D = 2
    GRADE_C = 3
    GRADE_B_MINUS = 4
    GRADE_B = 5
    GRADE_B_PLUS = 6
    GRADE_A_MINUS = 7
    GRADE_A = 8
    GRADE_A_PLUS = 9
    GRADE_S = 10
    GRADE_SS = 11
    GRADE_SSS = 12

    GRADE_CHOICES = [
        (GRADE_F, 'F'),
        (GRADE_D, 'D'),
        (GRADE_C, 'C'),
        (GRADE_B_MINUS, 'B-'),
        (GRADE_B, 'B'),
        (GRADE_B_PLUS, 'B+'),
        (GRADE_A_MINUS, 'A-'),
        (GRADE_A, 'A'),
        (GRADE_A_PLUS, 'A+'),
        (GRADE_S, 'S'),
        (GRADE_SS, 'SS'),
        (GRADE_SSS, 'SSS'),
    ]

    RAID_WATER = 1001
    RAID_FIRE = 2001
    RAID_WIND = 3001
    RAID_LIGHT = 4001
    RAID_DARK = 5001

    RAID_CHOICES = [
        (RAID_WATER, 'Ice Beast'),
        (RAID_FIRE, 'Fire Beast'),
        (RAID_WIND, 'Wind Beast'),
        (RAID_LIGHT, 'Light Beast'),
        (RAID_DARK, 'Dark Beast'),
    ]

    RAID_DICT = {raid[0]: raid[1] for raid in RAID_CHOICES}

    RAID_SLUGS = {
        'ice-beast': RAID_WATER,
        'fire-beast': RAID_FIRE,
        'wind-beast': RAID_WIND,
        'light-beast': RAID_LIGHT,
        'dark-beast': RAID_DARK,
    }

    RAID_ICONS = {
        RAID_WATER: '/icons/rift_water.png',
        RAID_FIRE: '/icons/rift_fire.png',
        RAID_WIND: '/icons/rift_wind.png',
        RAID_LIGHT: '/icons/rift_light.png',
        RAID_DARK: '/icons/rift_dark.png',
    }

    dungeon = models.IntegerField(choices=RAID_CHOICES)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    total_damage = models.IntegerField()
    success = models.BooleanField()
    mana = models.IntegerField(default=0)

    def __unicode__(self):
        return ' '.join([self.get_dungeon_display(), self.get_grade_display(), str(self.summoner)])


# Rune Crafting
class RuneCraft(RuneDrop):
    log = models.ForeignKey('RuneCraftLog', related_name='rune')


class RuneCraftLog(LogEntry):
    CRAFT_LOW = 0
    CRAFT_MID = 1
    CRAFT_HIGH = 2

    CRAFT_CHOICES = [
        (CRAFT_LOW, 'Low'),
        (CRAFT_MID, 'Mid'),
        (CRAFT_HIGH, 'High'),
    ]

    craft_level = models.IntegerField(choices=CRAFT_CHOICES)


# Shop Refreshing
class ShopRefreshRune(RuneDrop):
    log = models.ForeignKey('ShopRefreshLog', related_name='rune_drops')
    cost = models.IntegerField()


class ShopRefreshItem(ItemDrop):
    log = models.ForeignKey('ShopRefreshLog', related_name='item_drops')
    cost = models.IntegerField()


class ShopRefreshMonster(MonsterDrop):
    log = models.ForeignKey('ShopRefreshLog', related_name='monster_drops')
    cost = models.IntegerField()


class ShopRefreshLog(LogEntry):
    slots_available = models.IntegerField(blank=True, null=True)


# World Boss
class WorldBossMonsterDrop(MonsterDrop):
    log = models.ForeignKey('WorldBossLog', related_name='monster_drops')


class WorldBossItemDrop(ItemDrop):
    log = models.ForeignKey('WorldBossLog', related_name='item_drops')


class WorldBossRuneDrop(RuneDrop):
    log = models.ForeignKey('WorldBossLog', related_name='rune_drops')


class WorldBossLog(LogEntry):
    GRADE_F = 1
    GRADE_D = 2
    GRADE_C = 3
    GRADE_B_MINUS = 4
    GRADE_B = 5
    GRADE_B_PLUS = 6
    GRADE_A_MINUS = 7
    GRADE_A = 8
    GRADE_A_PLUS = 9
    GRADE_S = 10
    GRADE_SS = 11
    GRADE_SSS = 12

    GRADE_CHOICES = [
        (GRADE_F, 'F'),
        (GRADE_D, 'D'),
        (GRADE_C, 'C'),
        (GRADE_B_MINUS, 'B-'),
        (GRADE_B, 'B'),
        (GRADE_B_PLUS, 'B+'),
        (GRADE_A_MINUS, 'A-'),
        (GRADE_A, 'A'),
        (GRADE_A_PLUS, 'A+'),
        (GRADE_S, 'S'),
        (GRADE_SS, 'SS'),
        (GRADE_SSS, 'SSS'),
    ]

    battle_key = models.BigIntegerField(null=True, blank=True)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    damage = models.IntegerField()
    battle_points = models.IntegerField()
    bonus_battle_points = models.IntegerField()
    avg_monster_level = models.FloatField()
    monster_count = models.IntegerField()


# Rift of Worlds
class RiftRaidItemDrop(ItemDrop):
    log = models.ForeignKey('RiftRaidLog')
    wizard_id = models.BigIntegerField()
    battle_key = models.BigIntegerField(db_index=True)


class RiftRaidMonsterDrop(MonsterDrop):
    log = models.ForeignKey('RiftRaidLog')
    wizard_id = models.BigIntegerField()
    battle_key = models.BigIntegerField(db_index=True)


class RiftRaidRuneCraftDrop(RuneCraftDrop):
    log = models.ForeignKey('RiftRaidLog')
    wizard_id = models.BigIntegerField()
    battle_key = models.BigIntegerField(db_index=True)


class RiftRaidLog(LogEntry):
    DIFFICULTY_R1 = 1
    DIFFICULTY_R2 = 2
    DIFFICULTY_R3 = 3
    DIFFICULTY_R4 = 4
    DIFFICULTY_R5 = 5

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_R1, 'R1'),
        (DIFFICULTY_R2, 'R2'),
        (DIFFICULTY_R3, 'R3'),
        (DIFFICULTY_R4, 'R4'),
        (DIFFICULTY_R5, 'R5'),
    ]

    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    raid = models.IntegerField()
    action_item = models.IntegerField()  # Not sure what this is yet. Recording just in case.
    success = models.NullBooleanField()  # Null value here is an incomplete record from a log that needs the start and result commands to fill in completely
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    contribution = models.IntegerField(blank=True, null=True)


# Export management
class ExportManager(models.Model):
    export_category = models.TextField()
    last_row = models.BigIntegerField(default=0)
