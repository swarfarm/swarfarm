from functools import partial
from itertools import zip_longest
from math import floor
from operator import is_not

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from . import base


class RuneObjectBase(base.Stats, base.Quality):
    # Provides basic rune related constants
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

    TYPE_CHOICES = (
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
    )

    STAR_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    )

    # Mappings from com2us' API data to model defined values
    COM2US_TYPE_MAP = {
        1: TYPE_ENERGY,
        2: TYPE_GUARD,
        3: TYPE_SWIFT,
        4: TYPE_BLADE,
        5: TYPE_RAGE,
        6: TYPE_FOCUS,
        7: TYPE_ENDURE,
        8: TYPE_FATAL,
        10: TYPE_DESPAIR,
        11: TYPE_VAMPIRE,
        13: TYPE_VIOLENT,
        14: TYPE_NEMESIS,
        15: TYPE_WILL,
        16: TYPE_SHIELD,
        17: TYPE_REVENGE,
        18: TYPE_DESTROY,
        19: TYPE_FIGHT,
        20: TYPE_DETERMINATION,
        21: TYPE_ENHANCE,
        22: TYPE_ACCURACY,
        23: TYPE_TOLERANCE,
    }


class Rune(models.Model, RuneObjectBase):
    MAIN_STAT_VALUES = {
        # [stat][stars][level]: value
        RuneObjectBase.STAT_HP: {
            1: [40, 85, 130, 175, 220, 265, 310, 355, 400, 445, 490, 535, 580, 625, 670, 804],
            2: [70, 130, 190, 250, 310, 370, 430, 490, 550, 610, 670, 730, 790, 850, 910, 1092],
            3: [100, 175, 250, 325, 400, 475, 550, 625, 700, 775, 850, 925, 1000, 1075, 1150, 1380],
            4: [160, 250, 340, 430, 520, 610, 700, 790, 880, 970, 1060, 1150, 1240, 1330, 1420, 1704],
            5: [270, 375, 480, 585, 690, 795, 900, 1005, 1110, 1215, 1320, 1425, 1530, 1635, 1740, 2088],
            6: [360, 480, 600, 720, 840, 960, 1080, 1200, 1320, 1440, 1560, 1680, 1800, 1920, 2040, 2448],
        },
        RuneObjectBase.STAT_HP_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        RuneObjectBase.STAT_ATK: {
            1: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
            2: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
            3: [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
            4: [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
            5: [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
            6: [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160],
        },
        RuneObjectBase.STAT_ATK_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        RuneObjectBase.STAT_DEF: {
            1: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
            2: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
            3: [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
            4: [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
            5: [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
            6: [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160],
        },
        RuneObjectBase.STAT_DEF_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        RuneObjectBase.STAT_SPD: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 25],
            4: [4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 30],
            5: [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 39],
            6: [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 42],
        },
        RuneObjectBase.STAT_CRIT_RATE_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
            4: [4, 6, 8, 11, 13, 15, 17, 19, 22, 24, 26, 28, 30, 33, 35, 41],
            5: [5, 7, 10, 12, 15, 17, 19, 22, 24, 27, 29, 31, 34, 36, 39, 47],
            6: [7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 58],
        },
        RuneObjectBase.STAT_CRIT_DMG_PCT: {
            1: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            2: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
            3: [4, 6, 9, 11, 13, 16, 18, 20, 22, 25, 27, 29, 32, 34, 36, 43],
            4: [6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 57],
            5: [8, 11, 15, 18, 21, 25, 28, 31, 34, 38, 41, 44, 48, 51, 54, 65],
            6: [11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67, 80],
        },
        RuneObjectBase.STAT_RESIST_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
            5: [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
            6: [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64],
        },
        RuneObjectBase.STAT_ACCURACY_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
            5: [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
            6: [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64],
        },
    }

    MAIN_STATS_BY_SLOT = {
        1: [
            RuneObjectBase.STAT_ATK,
        ],
        2: [
            RuneObjectBase.STAT_ATK,
            RuneObjectBase.STAT_ATK_PCT,
            RuneObjectBase.STAT_DEF,
            RuneObjectBase.STAT_DEF_PCT,
            RuneObjectBase.STAT_HP,
            RuneObjectBase.STAT_HP_PCT,
            RuneObjectBase.STAT_SPD,
        ],
        3: [
            RuneObjectBase.STAT_DEF,
        ],
        4: [
            RuneObjectBase.STAT_ATK,
            RuneObjectBase.STAT_ATK_PCT,
            RuneObjectBase.STAT_DEF,
            RuneObjectBase.STAT_DEF_PCT,
            RuneObjectBase.STAT_HP,
            RuneObjectBase.STAT_HP_PCT,
            RuneObjectBase.STAT_CRIT_RATE_PCT,
            RuneObjectBase.STAT_CRIT_DMG_PCT,
        ],
        5: [
            RuneObjectBase.STAT_HP,
        ],
        6: [
            RuneObjectBase.STAT_ATK,
            RuneObjectBase.STAT_ATK_PCT,
            RuneObjectBase.STAT_DEF,
            RuneObjectBase.STAT_DEF_PCT,
            RuneObjectBase.STAT_HP,
            RuneObjectBase.STAT_HP_PCT,
            RuneObjectBase.STAT_RESIST_PCT,
            RuneObjectBase.STAT_ACCURACY_PCT,
        ]
    }

    SUBSTAT_INCREMENTS = {
        # [stat][stars]: value
        RuneObjectBase.STAT_HP: {
            1: 60,
            2: 105,
            3: 165,
            4: 225,
            5: 300,
            6: 375,
        },
        RuneObjectBase.STAT_HP_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_ATK: {
            1: 4,
            2: 5,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
        },
        RuneObjectBase.STAT_ATK_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_DEF: {
            1: 4,
            2: 5,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
        },
        RuneObjectBase.STAT_DEF_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_SPD: {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
        },
        RuneObjectBase.STAT_CRIT_RATE_PCT: {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
        },
        RuneObjectBase.STAT_CRIT_DMG_PCT: {
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
        },
        RuneObjectBase.STAT_RESIST_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_ACCURACY_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
    }

    UPGRADE_VALUES = {
        rune_type: {
            stars: value/level_data[6]
            for stars, value in level_data.items()
        }
        for rune_type, level_data in SUBSTAT_INCREMENTS.items()
    }

    INNATE_STAT_TITLES = {
        RuneObjectBase.STAT_HP: 'Strong',
        RuneObjectBase.STAT_HP_PCT: 'Tenacious',
        RuneObjectBase.STAT_ATK: 'Ferocious',
        RuneObjectBase.STAT_ATK_PCT: 'Powerful',
        RuneObjectBase.STAT_DEF: 'Sturdy',
        RuneObjectBase.STAT_DEF_PCT: 'Durable',
        RuneObjectBase.STAT_SPD: 'Quick',
        RuneObjectBase.STAT_CRIT_RATE_PCT: 'Mortal',
        RuneObjectBase.STAT_CRIT_DMG_PCT: 'Cruel',
        RuneObjectBase.STAT_RESIST_PCT: 'Resistant',
        RuneObjectBase.STAT_ACCURACY_PCT: 'Intricate',
    }

    RUNE_SET_COUNT_REQUIREMENTS = {
        RuneObjectBase.TYPE_ENERGY: 2,
        RuneObjectBase.TYPE_FATAL: 4,
        RuneObjectBase.TYPE_BLADE: 2,
        RuneObjectBase.TYPE_RAGE: 4,
        RuneObjectBase.TYPE_SWIFT: 4,
        RuneObjectBase.TYPE_FOCUS: 2,
        RuneObjectBase.TYPE_GUARD: 2,
        RuneObjectBase.TYPE_ENDURE: 2,
        RuneObjectBase.TYPE_VIOLENT: 4,
        RuneObjectBase.TYPE_WILL: 2,
        RuneObjectBase.TYPE_NEMESIS: 2,
        RuneObjectBase.TYPE_SHIELD: 2,
        RuneObjectBase.TYPE_REVENGE: 2,
        RuneObjectBase.TYPE_DESPAIR: 4,
        RuneObjectBase.TYPE_VAMPIRE: 4,
        RuneObjectBase.TYPE_DESTROY: 2,
        RuneObjectBase.TYPE_FIGHT: 2,
        RuneObjectBase.TYPE_DETERMINATION: 2,
        RuneObjectBase.TYPE_ENHANCE: 2,
        RuneObjectBase.TYPE_ACCURACY: 2,
        RuneObjectBase.TYPE_TOLERANCE: 2,
    }

    RUNE_SET_BONUSES = {
        RuneObjectBase.TYPE_ENERGY: {
            'count': 2,
            'stat': RuneObjectBase.STAT_HP_PCT,
            'value': 15.0,
            'team': False,
            'description': '2 Set: HP +15%',
        },
        RuneObjectBase.TYPE_FATAL: {
            'count': 4,
            'stat': RuneObjectBase.STAT_ATK_PCT,
            'value': 35.0,
            'team': False,
            'description': '4 Set: Attack Power +35%',
        },
        RuneObjectBase.TYPE_BLADE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_CRIT_RATE_PCT,
            'value': 12.0,
            'team': False,
            'description': '2 Set: Critical Rate +12%',
        },
        RuneObjectBase.TYPE_RAGE: {
            'count': 4,
            'stat': RuneObjectBase.STAT_CRIT_DMG_PCT,
            'value': 40.0,
            'team': False,
            'description': '4 Set: Critical Damage +40%',
        },
        RuneObjectBase.TYPE_SWIFT: {
            'count': 4,
            'stat': RuneObjectBase.STAT_SPD,
            'value': 25.0,
            'team': False,
            'description': '4 Set: Attack Speed +25%',
        },
        RuneObjectBase.TYPE_FOCUS: {
            'count': 2,
            'stat': RuneObjectBase.STAT_ACCURACY_PCT,
            'value': 20.0,
            'team': False,
            'description': '2 Set: Accuracy +20%',
        },
        RuneObjectBase.TYPE_GUARD: {
            'count': 2,
            'stat': RuneObjectBase.STAT_DEF_PCT,
            'value': 15.0,
            'team': False,
            'description': '2 Set: Defense +15%',
        },
        RuneObjectBase.TYPE_ENDURE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_RESIST_PCT,
            'value': 20.0,
            'team': False,
            'description': '2 Set: Resistance +20%',
        },
        RuneObjectBase.TYPE_VIOLENT: {
            'count': 4,
            'stat': None,
            'value': None,
            'team': False,
            'description': '4 Set: Get Extra Turn +22%',
        },
        RuneObjectBase.TYPE_WILL: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': '2 Set: Immunity +1 turn',
        },
        RuneObjectBase.TYPE_NEMESIS: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': '2 Set: ATK Gauge +4% (for every 7% HP lost)',
        },
        RuneObjectBase.TYPE_SHIELD: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': True,
            'description': '2 Set: Ally Shield 3 turns (15% of HP)',
        },
        RuneObjectBase.TYPE_REVENGE: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': '2 Set: Counterattack +15%',
        },
        RuneObjectBase.TYPE_DESPAIR: {
            'count': 4,
            'stat': None,
            'value': None,
            'team': False,
            'description': '4 Set: Stun Rate +25%',
        },
        RuneObjectBase.TYPE_VAMPIRE: {
            'count': 4,
            'stat': None,
            'value': None,
            'team': False,
            'description': '4 Set: Life Drain +35%',
        },
        RuneObjectBase.TYPE_DESTROY: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': "2 Set: 30% of the damage dealt will reduce up to 4% of the enemy's Max HP",
        },
        RuneObjectBase.TYPE_FIGHT: {
            'count': 2,
            'stat': RuneObjectBase.STAT_ATK,
            'value': 8.0,
            'team': True,
            'description': '2 Set: Increase the Attack Power of all allies by 8%',
        },
        RuneObjectBase.TYPE_DETERMINATION: {
            'count': 2,
            'stat': RuneObjectBase.STAT_DEF,
            'value': 8.0,
            'team': True,
            'description': '2 Set: Increase the Defense of all allies by 8%',
        },
        RuneObjectBase.TYPE_ENHANCE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_HP,
            'value': 8.0,
            'team': True,
            'description': '2 Set: Increase the HP of all allies by 8%',
        },
        RuneObjectBase.TYPE_ACCURACY: {
            'count': 2,
            'stat': RuneObjectBase.STAT_ACCURACY_PCT,
            'value': 10.0,
            'team': True,
            'description': '2 Set: Increase the Accuracy of all allies by 10%',
        },
        RuneObjectBase.TYPE_TOLERANCE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_RESIST_PCT,
            'value': 10.0,
            'team': True,
            'description': '2 Set: Increase the Resistance of all allies by 10%',
        },
    }

    type = models.IntegerField(choices=RuneObjectBase.TYPE_CHOICES)
    stars = models.IntegerField()
    level = models.IntegerField()
    slot = models.IntegerField()
    quality = models.IntegerField(default=0, choices=RuneObjectBase.QUALITY_CHOICES)
    original_quality = models.IntegerField(choices=RuneObjectBase.QUALITY_CHOICES, blank=True, null=True)
    ancient = models.BooleanField(default=False)
    value = models.IntegerField(blank=True, null=True)
    main_stat = models.IntegerField(choices=RuneObjectBase.STAT_CHOICES)
    main_stat_value = models.IntegerField()
    innate_stat = models.IntegerField(choices=RuneObjectBase.STAT_CHOICES, null=True, blank=True)
    innate_stat_value = models.IntegerField(null=True, blank=True)
    substats = ArrayField(
        models.IntegerField(choices=RuneObjectBase.STAT_CHOICES, null=True, blank=True),
        size=4,
        default=list,
    )
    substat_values = ArrayField(
        models.IntegerField(blank=True, null=True),
        size=4,
        default=list,
    )
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

    # The following fields exist purely to allow easier filtering and are updated on model save
    has_hp = models.BooleanField(default=False)
    has_atk = models.BooleanField(default=False)
    has_def = models.BooleanField(default=False)
    has_crit_rate = models.BooleanField(default=False)
    has_crit_dmg = models.BooleanField(default=False)
    has_speed = models.BooleanField(default=False)
    has_resist = models.BooleanField(default=False)
    has_accuracy = models.BooleanField(default=False)
    efficiency = models.FloatField(blank=True, null=True)
    max_efficiency = models.FloatField(blank=True, null=True)
    substat_upgrades_remaining = models.IntegerField(blank=True, null=True)
    has_grind = models.IntegerField(default=0, help_text='Number of grindstones applied')
    has_gem = models.BooleanField(default=False, help_text='Has had an enchant gem applied')

    class Meta:
        abstract = True

    def get_main_stat_rune_display(self):
        return RuneObjectBase.STAT_DISPLAY.get(self.main_stat, '')

    def get_innate_stat_rune_display(self):
        return RuneObjectBase.STAT_DISPLAY.get(self.innate_stat, '')

    def get_innate_stat_title(self):
        if self.innate_stat is not None:
            return self.INNATE_STAT_TITLES[self.innate_stat]
        else:
            return ''

    def get_substat_rune_display(self, idx):
        if len(self.substats) > idx:
            return RuneObjectBase.STAT_DISPLAY.get(self.substats[idx], '')
        else:
            return ''

    # For template rendering
    @property
    def substat_rune_display(self):
        return [self.get_substat_rune_display(x) for x in range(len(self.substats))]

    def get_stat(self, stat_type, sub_stats_only=False):
        if self.main_stat == stat_type and not sub_stats_only:
            return self.main_stat_value
        elif self.innate_stat == stat_type and not sub_stats_only:
            return self.innate_stat_value
        else:
            for idx, substat in enumerate(self.substats):
                if substat == stat_type:
                    return self.substat_values[idx] + self.substats_grind_value[idx]

        return 0

    # Individual functions for each stat to use within templates
    def get_hp_pct(self):
        return self.get_stat(Rune.STAT_HP_PCT, False)

    def get_hp(self):
        return self.get_stat(Rune.STAT_HP, False)

    def get_def_pct(self):
        return self.get_stat(Rune.STAT_DEF_PCT, False)

    def get_def(self):
        return self.get_stat(Rune.STAT_DEF, False)

    def get_atk_pct(self):
        return self.get_stat(Rune.STAT_ATK_PCT, False)

    def get_atk(self):
        return self.get_stat(Rune.STAT_ATK, False)

    def get_spd(self):
        return self.get_stat(Rune.STAT_SPD, False)

    def get_cri_rate(self):
        return self.get_stat(Rune.STAT_CRIT_RATE_PCT, False)

    def get_cri_dmg(self):
        return self.get_stat(Rune.STAT_CRIT_DMG_PCT, False)

    def get_res(self):
        return self.get_stat(Rune.STAT_RESIST_PCT, False)

    def get_acc(self):
        return self.get_stat(Rune.STAT_ACCURACY_PCT, False)

    @property
    def substat_upgrades_received(self):
        return int(floor(min(self.level, 12) / 3))

    def get_efficiency(self):
        # https://www.youtube.com/watch?v=SBWeptNNbYc
        # All runes are compared against max stat values for perfect 6* runes.

        # Main stat efficiency (max 100%)
        running_sum = float(self.MAIN_STAT_VALUES[self.main_stat][self.stars][15]) / float(
            self.MAIN_STAT_VALUES[self.main_stat][6][15])

        # Substat efficiencies (max 20% per; 1 innate, max 4 initial, 4 upgrades)
        if self.innate_stat is not None:
            running_sum += self.innate_stat_value / float(self.SUBSTAT_INCREMENTS[self.innate_stat][6] * 5)

        for substat, value, grind_value in zip(self.substats, self.substat_values, self.substats_grind_value):
            running_sum += (value + grind_value) / float(self.SUBSTAT_INCREMENTS[substat][6] * 5)

        return running_sum / 2.8 * 100

    def get_max_efficiency(self):
        # Max efficiency does not include grinds
        efficiency = self.get_efficiency()
        new_stats = min(4 - len(self.substats), self.substat_upgrades_remaining)
        old_stats = self.substat_upgrades_remaining - new_stats

        if old_stats > 0:
            # we can repeatedly upgrade the most value of the existing stats
            best_stat = max(
                0,  # ensure max() doesn't error if we only have one stat
                *[self.UPGRADE_VALUES[stat][self.stars] for stat in self.substats]
            )
            efficiency += best_stat * old_stats * 0.2 / 2.8 * 100

        if new_stats:
            # add the top N stats
            available_upgrades = sorted(
                [
                    upgrade_value[self.stars]
                    for stat, upgrade_value in self.UPGRADE_VALUES.items()
                    if stat not in self.substats
                ],
                reverse=True
            )
            efficiency += sum(available_upgrades[:new_stats]) * 0.2 / 2.8 * 100

        return efficiency

    def update_fields(self):
        # Set filterable fields
        rune_stat_types = [self.main_stat, self.innate_stat] + self.substats
        self.has_hp = any([i for i in rune_stat_types if i in [self.STAT_HP, self.STAT_HP_PCT]])
        self.has_atk = any([i for i in rune_stat_types if i in [self.STAT_ATK, self.STAT_ATK_PCT]])
        self.has_def = any([i for i in rune_stat_types if i in [self.STAT_DEF, self.STAT_DEF_PCT]])
        self.has_crit_rate = self.STAT_CRIT_RATE_PCT in rune_stat_types
        self.has_crit_dmg = self.STAT_CRIT_DMG_PCT in rune_stat_types
        self.has_speed = self.STAT_SPD in rune_stat_types
        self.has_resist = self.STAT_RESIST_PCT in rune_stat_types
        self.has_accuracy = self.STAT_ACCURACY_PCT in rune_stat_types

        self.quality = len([substat for substat in self.substats if substat])
        self.substat_upgrades_remaining = 4 - self.substat_upgrades_received
        self.efficiency = self.get_efficiency()
        self.max_efficiency = self.get_max_efficiency()
        self.has_grind = sum([bool(x) for x in self.substats_grind_value])
        self.has_gem = any(self.substats_enchanted)

        # Cap stat values to appropriate value
        # Very old runes can have different values, but never higher than the cap
        if self.main_stat_value:
            self.main_stat_value = min(self.MAIN_STAT_VALUES[self.main_stat][self.stars][self.level], self.main_stat_value)
        else:
            self.main_stat_value = self.MAIN_STAT_VALUES[self.main_stat][self.stars][self.level]

        if self.innate_stat and self.innate_stat_value and self.innate_stat_value > self.SUBSTAT_INCREMENTS[self.innate_stat][self.stars]:
            self.innate_stat_value = self.SUBSTAT_INCREMENTS[self.innate_stat][self.stars]

        for idx, substat in enumerate(self.substats):
            max_sub_value = self.SUBSTAT_INCREMENTS[substat][self.stars] * (self.substat_upgrades_received + 1)
            if self.substat_values[idx] > max_sub_value:
                self.substat_values[idx] = max_sub_value

    def clean(self):
        # Check slot, level, etc for valid ranges
        stars_message = 'Must be between 1 and 6'
        if self.stars is None:
            raise ValidationError({'stars': ValidationError(stars_message, code='stars_missing')})
        elif self.stars < 1 or self.stars > 6:
            raise ValidationError({'stars': ValidationError(stars_message, code='stars_invalid')})

        level_message = 'Must be between 0 and 15'
        if self.level is None:
            raise ValidationError({'level': ValidationError(level_message, code='level_missing')})
        elif self.level < 0 or self.level > 15:
            raise ValidationError({'level': ValidationError(level_message, code='level_invalid')})

        slot_message = 'Must be between 1 and 6'
        if self.slot is None:
            raise ValidationError({'slot': ValidationError(slot_message, code='slot_missing')})
        elif self.slot < 1 or self.slot > 6:
            raise ValidationError({'slot': ValidationError(slot_message, code='slot_invalid')})

        # Check main stat is appropriate for this slot
        if self.slot and self.main_stat not in self.MAIN_STATS_BY_SLOT[self.slot]:
            raise ValidationError({
                'main_stat': ValidationError(
                    'Unacceptable stat for slot %(slot)s. Must be %(valid_stats)s.',
                    params={
                        'slot': self.slot,
                        'valid_stats': ', '.join([RuneObjectBase.STAT_CHOICES[stat - 1][1] for stat in self.MAIN_STATS_BY_SLOT[self.slot]])
                    },
                    code='invalid_main_stat_for_slot'
                ),
            })

        # Check that the same stat type was not used multiple times
        stat_list = list(filter(
            partial(is_not, None),
            [self.main_stat, self.innate_stat] + self.substats
        ))
        if len(stat_list) != len(set(stat_list)):
            raise ValidationError(
                'All stats and substats must be unique.',
                code='duplicate_stats'
            )

        # Check if stat type was specified that it has value > 0
        if self.main_stat_value is None:
            raise ValidationError({
                'main_stat_value': ValidationError(
                    'Missing main stat value.',
                    code='main_stat_missing',
                )
            })

        max_main_stat_value = self.MAIN_STAT_VALUES[self.main_stat][self.stars][self.level]
        if self.main_stat_value > max_main_stat_value:
            raise ValidationError({
                'main_stat_value': ValidationError(
                    f'Main stat value for {self.get_main_stat_display()} at {self.stars}* lv. {self.level} must be less than {max_main_stat_value}',
                    code='main_stat_too_high',
                )
            })

        if self.innate_stat is not None:
            if self.innate_stat_value is None:
                raise ValidationError({
                    'innate_stat_value': ValidationError(
                        'Missing value',
                        code='innate_stat_missing'
                    )
                })
            if self.innate_stat_value <= 0:
                raise ValidationError({
                    'innate_stat_value': ValidationError(
                        'Must be greater than 0',
                        code='innate_stat_too_low'
                    )
                })
            max_sub_value = self.SUBSTAT_INCREMENTS[self.innate_stat][self.stars]

            # TODO: Remove not ancient check once ancient max substat values are found
            if self.innate_stat_value > max_sub_value and not self.ancient:
                raise ValidationError({
                    'innate_stat_value': ValidationError(
                        'Must be less than or equal to %(max)s',
                        params={'max': max_sub_value},
                        code='innate_stat_too_high'
                    )
                })
        else:
            self.innate_stat_value = None

        # Check that a minimum number of substats are present based on the level
        if len(self.substats) < self.substat_upgrades_received:
            raise ValidationError({
                'substats': ValidationError(
                    'A lv. %(level)s rune requires at least %(upgrades)s substat(s)',
                    params={
                        'level': self.level,
                        'upgrades': self.substat_upgrades_received,
                    },
                    code='not_enough_substats'
                )
            })

        # Trim substat values to match length of defined substats
        num_substats = len(self.substats)
        self.substat_values = self.substat_values[0:num_substats]
        self.substats_enchanted = self.substats_enchanted[0:num_substats]
        self.substats_grind_value = self.substats_grind_value[0:num_substats]

        for index, (substat, value, enchanted, grind_value) in enumerate(zip_longest(
                self.substats,
                self.substat_values,
                self.substats_enchanted,
                self.substats_grind_value
        )):
            if value is None or value <= 0:
                raise ValidationError({
                    'substat_values': ValidationError(
                        'Substat %(nth)s: Must be greater than 0.',
                        params={'nth': index + 1},
                        code=f'substat_too_low'
                    )
                })

            max_sub_value = self.SUBSTAT_INCREMENTS[substat][self.stars] * (self.substat_upgrades_received + 1)
            # TODO: Remove not ancient check once ancient max substat values are found
            if value > max_sub_value and not self.ancient:
                raise ValidationError({
                    'substat_values': ValidationError(
                        f'Substat %(nth)s: Must be less than or equal to {max_sub_value}.',
                        params={'nth': index + 1},
                        code=f'substat_too_high'
                    )
                })

            # Ensure the optional substat arrays are equal length to number of substats
            if enchanted is None:
                if len(self.substats_grind_value) < len(self.substats):
                    self.substats_enchanted.append(False)

            if grind_value is None:
                if len(self.substats_grind_value) < len(self.substats):
                    self.substats_grind_value.append(0)
                grind_value = 0

                # Validate grind value
                max_grind_value = RuneCraft.CRAFT_VALUE_RANGES[RuneCraft.CRAFT_ANCIENT_GRINDSTONE][substat][RuneCraft.QUALITY_LEGEND]['max']
                if grind_value > max_grind_value:
                    raise ValidationError({
                        'substats_grind_value': ValidationError(
                            f'Substat Grind %(nth)s: Must be less than or equal to {max_grind_value}.',
                            params={'nth': index + 1},
                            code=f'grind_too_high'
                        )
                    })

            if self.level < 12 and (enchanted or grind_value):
                raise ValidationError({
                    'level': ValidationError(
                        'Level must be 12 or higher when grind/enchant is applied',
                        code='level_invalid'
                    )
                })

        # Validate number of gems applied
        if sum(self.substats_enchanted) > 1:
            raise ValidationError({
                'substats_enchanted': ValidationError(
                    'Only one substat may have an enchant gem applied.',
                    code='too_many_enchants',
                ),
            })

    def save(self, *args, **kwargs):
        self.update_fields()
        super(Rune, self).save(*args, **kwargs)

    def __str__(self):
        return self.get_innate_stat_title() + ' ' + self.get_type_display() + ' ' + 'Rune'


class RuneCraft(models.Model, RuneObjectBase):
    CRAFT_GRINDSTONE = 0
    CRAFT_ENCHANT_GEM = 1
    CRAFT_IMMEMORIAL_GRINDSTONE = 2
    CRAFT_IMMEMORIAL_GEM = 3
    CRAFT_ANCIENT_GRINDSTONE = 4
    CRAFT_ANCIENT_GEM = 5

    CRAFT_CHOICES = (
        (CRAFT_GRINDSTONE, 'Grindstone'),
        (CRAFT_ENCHANT_GEM, 'Enchant Gem'),
        (CRAFT_IMMEMORIAL_GRINDSTONE, 'Immemorial Grindstone'),
        (CRAFT_IMMEMORIAL_GEM, 'Immemorial Gem'),
        (CRAFT_ANCIENT_GRINDSTONE, 'Ancient Grindstone'),
        (CRAFT_ANCIENT_GEM, 'Ancient Gem'),
    )

    CRAFT_ENCHANT_GEMS = [
        CRAFT_ENCHANT_GEM,
        CRAFT_IMMEMORIAL_GEM,
        CRAFT_ANCIENT_GEM,
    ]

    CRAFT_GRINDSTONES = [
        CRAFT_GRINDSTONE,
        CRAFT_IMMEMORIAL_GRINDSTONE,
        CRAFT_ANCIENT_GRINDSTONE,
    ]

    # Type > Stat > Quality > Min/Max
    CRAFT_VALUE_RANGES = {
        CRAFT_GRINDSTONE: {
            RuneObjectBase.STAT_HP: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 80, 'max': 120},
                RuneObjectBase.QUALITY_MAGIC: {'min': 100, 'max': 200},
                RuneObjectBase.QUALITY_RARE: {'min': 180, 'max': 250},
                RuneObjectBase.QUALITY_HERO: {'min': 230, 'max': 450},
                RuneObjectBase.QUALITY_LEGEND: {'min': 430, 'max': 550},
            },
            RuneObjectBase.STAT_HP_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneObjectBase.STAT_ATK: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 4, 'max': 8},
                RuneObjectBase.QUALITY_MAGIC: {'min': 6, 'max': 12},
                RuneObjectBase.QUALITY_RARE: {'min': 10, 'max': 18},
                RuneObjectBase.QUALITY_HERO: {'min': 12, 'max': 22},
                RuneObjectBase.QUALITY_LEGEND: {'min': 18, 'max': 30},
            },
            RuneObjectBase.STAT_ATK_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneObjectBase.STAT_DEF: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 4, 'max': 8},
                RuneObjectBase.QUALITY_MAGIC: {'min': 6, 'max': 12},
                RuneObjectBase.QUALITY_RARE: {'min': 10, 'max': 18},
                RuneObjectBase.QUALITY_HERO: {'min': 12, 'max': 22},
                RuneObjectBase.QUALITY_LEGEND: {'min': 18, 'max': 30},
            },
            RuneObjectBase.STAT_DEF_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneObjectBase.STAT_SPD: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_MAGIC: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 3},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 4},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 5},
            },
            RuneObjectBase.STAT_CRIT_RATE_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_MAGIC: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
            },
            RuneObjectBase.STAT_CRIT_DMG_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 7},
            },
            RuneObjectBase.STAT_RESIST_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
            RuneObjectBase.STAT_ACCURACY_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
        },
        CRAFT_ENCHANT_GEM: {
            RuneObjectBase.STAT_HP: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 100, 'max': 150},
                RuneObjectBase.QUALITY_MAGIC: {'min': 130, 'max': 220},
                RuneObjectBase.QUALITY_RARE: {'min': 200, 'max': 310},
                RuneObjectBase.QUALITY_HERO: {'min': 290, 'max': 420},
                RuneObjectBase.QUALITY_LEGEND: {'min': 400, 'max': 580},
            },
            RuneObjectBase.STAT_HP_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneObjectBase.STAT_ATK: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 8, 'max': 12},
                RuneObjectBase.QUALITY_MAGIC: {'min': 10, 'max': 16},
                RuneObjectBase.QUALITY_RARE: {'min': 15, 'max': 23},
                RuneObjectBase.QUALITY_HERO: {'min': 20, 'max': 30},
                RuneObjectBase.QUALITY_LEGEND: {'min': 28, 'max': 40},
            },
            RuneObjectBase.STAT_ATK_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneObjectBase.STAT_DEF: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 8, 'max': 12},
                RuneObjectBase.QUALITY_MAGIC: {'min': 10, 'max': 16},
                RuneObjectBase.QUALITY_RARE: {'min': 15, 'max': 23},
                RuneObjectBase.QUALITY_HERO: {'min': 20, 'max': 30},
                RuneObjectBase.QUALITY_LEGEND: {'min': 28, 'max': 40},
            },
            RuneObjectBase.STAT_DEF_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneObjectBase.STAT_SPD: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 10},
            },
            RuneObjectBase.STAT_CRIT_RATE_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 6, 'max': 9},
            },
            RuneObjectBase.STAT_CRIT_DMG_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 4, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 10},
            },
            RuneObjectBase.STAT_RESIST_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 6, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 11},
            },
            RuneObjectBase.STAT_ACCURACY_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 6, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 11},
            },
        },
        CRAFT_ANCIENT_GRINDSTONE: {
            RuneObjectBase.STAT_HP: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 80, 'max': 180},
                RuneObjectBase.QUALITY_MAGIC: {'min': 100, 'max': 260},
                RuneObjectBase.QUALITY_RARE: {'min': 180, 'max': 310},
                RuneObjectBase.QUALITY_HERO: {'min': 230, 'max': 510},
                RuneObjectBase.QUALITY_LEGEND: {'min': 430, 'max': 610},
            },
            RuneObjectBase.STAT_HP_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 5},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 12},
            },
            RuneObjectBase.STAT_ATK: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 4, 'max': 12},
                RuneObjectBase.QUALITY_MAGIC: {'min': 6, 'max': 16},
                RuneObjectBase.QUALITY_RARE: {'min': 10, 'max': 22},
                RuneObjectBase.QUALITY_HERO: {'min': 12, 'max': 26},
                RuneObjectBase.QUALITY_LEGEND: {'min': 18, 'max': 34},
            },
            RuneObjectBase.STAT_ATK_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 5},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 12},
            },
            RuneObjectBase.STAT_DEF: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 4, 'max': 12},
                RuneObjectBase.QUALITY_MAGIC: {'min': 6, 'max': 16},
                RuneObjectBase.QUALITY_RARE: {'min': 10, 'max': 22},
                RuneObjectBase.QUALITY_HERO: {'min': 12, 'max': 26},
                RuneObjectBase.QUALITY_LEGEND: {'min': 18, 'max': 34},
            },
            RuneObjectBase.STAT_DEF_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 5},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 12},
            },
            RuneObjectBase.STAT_SPD: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
            },
            RuneObjectBase.STAT_CRIT_RATE_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_MAGIC: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
            },
            RuneObjectBase.STAT_CRIT_DMG_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 7},
            },
            RuneObjectBase.STAT_RESIST_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
            RuneObjectBase.STAT_ACCURACY_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
        },
        CRAFT_ANCIENT_GEM: {
            RuneObjectBase.STAT_HP: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 100, 'max': 210},
                RuneObjectBase.QUALITY_MAGIC: {'min': 130, 'max': 280},
                RuneObjectBase.QUALITY_RARE: {'min': 200, 'max': 370},
                RuneObjectBase.QUALITY_HERO: {'min': 290, 'max': 480},
                RuneObjectBase.QUALITY_LEGEND: {'min': 400, 'max': 640},
            },
            RuneObjectBase.STAT_HP_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 6},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 9},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 11},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 13},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 15},
            },
            RuneObjectBase.STAT_ATK: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 8, 'max': 16},
                RuneObjectBase.QUALITY_MAGIC: {'min': 10, 'max': 20},
                RuneObjectBase.QUALITY_RARE: {'min': 15, 'max': 27},
                RuneObjectBase.QUALITY_HERO: {'min': 20, 'max': 34},
                RuneObjectBase.QUALITY_LEGEND: {'min': 28, 'max': 44},
            },
            RuneObjectBase.STAT_ATK_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 6},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 9},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 11},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 13},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 15},
            },
            RuneObjectBase.STAT_DEF: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 8, 'max': 16},
                RuneObjectBase.QUALITY_MAGIC: {'min': 10, 'max': 20},
                RuneObjectBase.QUALITY_RARE: {'min': 15, 'max': 27},
                RuneObjectBase.QUALITY_HERO: {'min': 20, 'max': 34},
                RuneObjectBase.QUALITY_LEGEND: {'min': 28, 'max': 44},
            },
            RuneObjectBase.STAT_DEF_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 6},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 9},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 11},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 13},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 15},
            },
            RuneObjectBase.STAT_SPD: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 11},
            },
            RuneObjectBase.STAT_CRIT_RATE_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
                RuneObjectBase.QUALITY_LEGEND: {'min': 6, 'max': 10},
            },
            RuneObjectBase.STAT_CRIT_DMG_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 6},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 4, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 5, 'max': 10},
                RuneObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 12},
            },
            RuneObjectBase.STAT_RESIST_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 6},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 8},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 10},
                RuneObjectBase.QUALITY_HERO: {'min': 6, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 13},
            },
            RuneObjectBase.STAT_ACCURACY_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 6},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 8},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 10},
                RuneObjectBase.QUALITY_HERO: {'min': 6, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 13},
            },
        },
    }
    CRAFT_VALUE_RANGES[CRAFT_IMMEMORIAL_GEM] = CRAFT_VALUE_RANGES[CRAFT_ENCHANT_GEM]
    CRAFT_VALUE_RANGES[CRAFT_IMMEMORIAL_GRINDSTONE] = CRAFT_VALUE_RANGES[CRAFT_GRINDSTONE]

    # Mappings from com2us' API data to model defined values
    COM2US_CRAFT_TYPE_MAP = {
        1: CRAFT_ENCHANT_GEM,
        2: CRAFT_GRINDSTONE,
        3: CRAFT_IMMEMORIAL_GEM,
        4: CRAFT_IMMEMORIAL_GRINDSTONE,
        5: CRAFT_ANCIENT_GEM,
        6: CRAFT_ANCIENT_GRINDSTONE,
    }

    type = models.IntegerField(choices=CRAFT_CHOICES)
    rune = models.IntegerField(choices=RuneObjectBase.TYPE_CHOICES, blank=True, null=True)
    stat = models.IntegerField(choices=RuneObjectBase.STAT_CHOICES)
    quality = models.IntegerField(choices=RuneObjectBase.QUALITY_CHOICES)
    value = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_min_value(self):
        try:
            return self.CRAFT_VALUE_RANGES[self.type][self.stat][self.quality]['min']
        except KeyError:
            return None
        except TypeError as e:
            print(e)
            return None

    def get_max_value(self):
        try:
            return self.CRAFT_VALUE_RANGES[self.type][self.stat][self.quality]['max']
        except KeyError:
            return None

    @staticmethod
    def get_valid_stats_for_type(craft_type):
        try:
            valid_stats = RuneCraft.CRAFT_VALUE_RANGES[craft_type].keys()
        except KeyError:
            return None
        else:
            stat_names = {stat: RuneObjectBase.STAT_CHOICES[stat - 1][1] for stat in valid_stats}

            return stat_names

    def __str__(self):
        if self.stat in RuneObjectBase.PERCENT_STATS:
            percent = '%'
        else:
            percent = ''

        return RuneCraft.STAT_DISPLAY.get(self.stat) + ' +' + str(self.get_min_value()) + percent + ' - ' + str(
            self.get_max_value()) + percent

